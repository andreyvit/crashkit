# -*- coding: utf-8
from datetime import date, datetime, timedelta
import time
import logging
import wsgiref.handlers
import os
import string
import urllib
import sets
import hashlib
from random import Random
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from django.utils import simplejson as json
from models import *
from commons import *

class ApiError(Exception):
  pass
  
def process_report(report):
  try:
    try:
      data = json.loads(report.data)
      occurrences = [ReportedOccurrence(report.product, report.client, item) for item in data]
    except ValueError, e:
      raise ApiError, e
    except KeyError, e:
      raise ApiError, e
    resulting_occurrences = []
    for occurrence in occurrences:
      resulting_occurrences.append(occurrence.submit())
    report.occurrences = map(lambda o: o.key(), resulting_occurrences)
    cases = group(lambda o: o.case, resulting_occurrences)
    
    bugs = []
    for case, case_occurrences in cases.iteritems():
      bugs.append(process_case(report.product, case, sum(map(lambda o: o.count_this_time, case_occurrences))))
    bugs = list(sets.Set(bugs))
    
    bugs_to_email = [b for b in bugs if b.should_spam()]
    if len(bugs_to_email) > 0:
      account = report.product.account
      product_path = 'http://crashkitapp.appspot.com/%s/products/%s' % (account.permalink, report.product.unique_name)
      
      e = (report.product.new_bug_notification_emails or '').strip()
      if len(e) > 0:
        emails = e.split(',')
        
        for bug in bugs_to_email:
          subject_bug_descr = "%s in %s.%s.%s:%s" % (bug.exception_name, bug.exception_package,
              bug.exception_klass, bug.exception_method, bug.exception_line)
          if bug.last_email_on is None:
            designator = 'NEW'
            tagline = "The following bug has occurred for the first time:"
          else:
            designator = 'RECURRING'
            tagline = "Just a friendly reminder that the following bug is still occurring:"
          subject = "[CrK %s/%s] %s %s" % (account.permalink, report.product.unique_name, designator, subject_bug_descr)
          
          body = u"""
  %(tagline)s

  Bug:        %(url)s
  Exception:  %(exception_name)s
  In:         %(exception_package)s.%(exception_klass)s.%(exception_method)s:%(exception_line)s
  Occurred:   %(occurrence_count)s
  Last time:  %(last_occurrence_on)s
              """ % dict(url='%s/bugs/%s/' % (product_path, bug.key().name()),
              tagline=tagline,
              exception_name=bug.exception_name,
              exception_package=bug.exception_package,
              exception_klass=bug.exception_klass,
              exception_method=bug.exception_method,
              exception_line=bug.exception_line,
              occurrence_count=decline(bug.occurrence_count, 'once', '# times'),
              last_occurrence_on=bug.last_occurrence_on)
      
          mail.send_mail('crashkit@yoursway.com', emails, subject, body)
    
          bug.last_email_on = datetime.now().date()
          bug.put()

  except ApiError, e:
    report.error = "%s: %s" % (e.__class__.__name__, e.message)
    report.status = REPORT_ERROR
    report.put()
    return
  report.status = REPORT_OK
  report.put()
  
def process_case(product, case, occurrence_count_delta):
  definitive_location = case.definitive_location(product)
  dummy_index, case.exception_name, case.exception_package, case.exception_klass, case.exception_method, case.exception_line = definitive_location
  
  location_salt = "%s|%s|%s|%s|%s|%d" % (case.language, case.exception_name, case.exception_package, case.exception_klass, case.exception_method, case.exception_line)
  location_hash = hashlib.sha1(location_salt).hexdigest()
  
  def txn(product_key):
    key_name = Bug.key_name_for(product_key.id_or_name(), location_hash)
    bug = Bug.get_by_key_name(key_name)
    if bug == None:
      bug = Bug(key_name=key_name, product=case.product, exception_name=case.exception_name,
          exception_package=case.exception_package, exception_klass=case.exception_klass,
          exception_method=case.exception_method, exception_line=case.exception_line,
          max_severity=case.severity, occurrence_count=case.occurrence_count,
          language=case.language,
          first_occurrence_on=case.first_occurrence_on, last_occurrence_on=case.last_occurrence_on,
          roles=case.roles, role_count=len(case.roles))
    else:
      bug.max_severity        = max(bug.max_severity, case.severity)
      bug.occurrence_count   += occurrence_count_delta
      bug.first_occurrence_on = min(bug.first_occurrence_on, case.first_occurrence_on)
      bug.last_occurrence_on  = max(bug.last_occurrence_on, case.last_occurrence_on)
      bug.roles               = list(sets.Set(bug.roles + case.roles))
      bug.role_count          = len(bug.roles)
    bug.put()
    return bug
  bug = db.run_in_transaction(txn, case.product.key())
  
  def txn(key):
    case = Case.get(key)
    case.bug = bug
    dummy_index, case.exception_name, case.exception_package, case.exception_klass, case.exception_method, case.exception_line = definitive_location
    case.put()
  db.run_in_transaction(txn, case.key())
  return bug

# class ExceptionInfo(object):
#   def __init__(self, name, locations):
#     self.name = name
#     self.locations = locations
#     
#   def __repr__(self):
#     return 'ExceptionInfo(%s, %s)' % (repr(name), repr(locations))
#   
# class javalocation(object):
#   def __init__(self, package, klass, method, line):
#     self.package = package
#     self.klass = klass
#     self.method = method
#     self.line = line
#     
#   def __repr__(self):
#     return 'javalocation(%s, %s, %s, %s)' % (repr(self.package), repr(self.klass), repr(self.method), repr(self.line))

@transaction
def create_or_update_case(case_hash, product, severity, context, date, count, role, language, exceptions_json):
  key_name = Case.key_name_for(product.key(), case_hash)
  case = Case.get_by_key_name(key_name)
  if case == None:
    case = Case(key_name=key_name, product=product, context=context,
      severity=severity, language=language, exceptions=exceptions_json,
      occurrence_count=count, first_occurrence_on=date, last_occurrence_on=date,
      roles=[role])
  else:
    case.occurrence_count += count
    if date < case.first_occurrence_on:
      case.first_occurrence_on = date
    if date > case.last_occurrence_on:
      case.last_occurrence_on = date
    if not role in case.roles:
      case.roles.append(role)
  case.put()
  return case

@transaction
def create_or_update_occurrence(occurrence_hash, case, client, date, messages, data, env, count, role):
  key_name = Occurrence.key_name_for(case.key().id_or_name(), client.key().id_or_name(), occurrence_hash)
  occurrence = Occurrence.get_by_key_name(key_name)
  if occurrence == None:
    occurrence = Occurrence(key_name=key_name, case=case, client=client, date=date, count=count,
        role=role)
    if messages:
      occurrence.exception_messages = messages
    for k, v in data.iteritems():
      setattr(occurrence, 'data_%s' % k, db.Text(unicode(v)))
    for k, v in env.iteritems():
      setattr(occurrence, 'env_%s' % k, db.Text(unicode(v)))
  else:
    occurrence.count += count
  occurrence.put()
  return occurrence
  
def parse_location(el):
  f = el.get('package', '')
  if f == '' or f is None:
    f = el.get('file', '')
    if f is None:
      f = ''
  k = el.get('class', '')
  m = el.get('method', '')
  if m == '':
    m = el.get('function', '')
  if k == '' or k is None:
    k = m
    m = ''
  lineno = el.get('line', 0)
  if lineno is None:
    lineno = 0
  return dict(package=f, klass=k, method=m, line=int(lineno))

class ReportedOccurrence(object):
  
  def __init__(self, product, client, data):
    self.product = product
    self.client = client
    if 'date' in data:
      self.date = date(*(time.strptime(data['date'], '%Y-%m-%d')[0:3]))
    else:
      self.date = date.today()
    self.count = int(data.get('count', 1))
    mm = [e.get('message', '') for e in data['exceptions']]
    self.exception_messages = [db.Text(x) for x in mm if len(x) > 0]
    self.severity = (2 if data.get('severity', 'normal') == 'major' else 1)
    self.context_name = data.get('userActionOrScreenNameOrBackgroundProcess', '')
    if self.context_name == '':
      self.context_name = 'unknown'
    self.role = data.get('role', 'customer')
    self.env = data.get('env', {})
    if isinstance(self.env, list):
      self.env = {} # fuck you, PHP
    self.data = data.get('data', {})
    if isinstance(self.data, list):
      self.data = {} # fuck you again
    self.language = data.get('language', 'unknown')
    self.exceptions = [
      dict(name=e['name'],
        locations=[parse_location(el) for el in e['locations']])
      for e in data['exceptions'] ]
   
  def submit(self):
    context = Context.get_or_insert(Context.key_name_for(self.product.key(), self.context_name),
        product=self.product, name=self.context_name)
    
    exceptions_json = repr(self.exceptions)
    case_salt = "%s|%s|%s|%s" % (self.severity, self.context_name, self.language, exceptions_json)
    case_hash = hashlib.sha1(case_salt).hexdigest()
    
    occurrence_salt = "%s|%s|%s|%s|%s|%s" % (case_hash, repr(self.exception_messages), repr(self.env), repr(self.data), self.date, self.role)
    occurrence_hash = hashlib.sha1(occurrence_salt).hexdigest()
    
    case = create_or_update_case(case_hash, self.product, self.severity, context, self.date, self.count, self.role, self.language, exceptions_json)
    occurrence = create_or_update_occurrence(occurrence_hash, case, self.client, self.date,
        self.exception_messages, self.data, self.env, self.count, self.role)
    occurrence.count_this_time = self.count
    return occurrence
