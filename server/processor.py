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
  
def send_email_notifications(bug, emails, account, product):
  product_path = 'http://crashkitapp.appspot.com/%s/products/%s' % (account.permalink, product.unique_name)
  subject_bug_descr = "%s in %s.%s.%s:%s" % (bug.exception_name, bug.exception_package,
      bug.exception_klass, bug.exception_method, bug.exception_line)
  if bug.last_email_on is None:
    designator = 'NEW'
    tagline = "The following bug has occurred for the first time:"
  else:
    designator = 'RECURRING'
    tagline = "Just a friendly reminder that the following bug is still occurring:"
  subject = "[CrK %s/%s] %s %s" % (account.permalink, product.unique_name, designator, subject_bug_descr)
  
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
  
def process_incoming_occurrence(product, client, incoming_occurrence):
  context = Context.get_or_insert(Context.key_name_for(product.key(), incoming_occurrence.context_name),
      product=product, name=incoming_occurrence.context_name)
      
  dummy_index, exception_name, exception_package, exception_klass, exception_method, exception_line = incoming_occurrence.definitive_location

  location_salt = "%s|%s|%s|%s|%s|%d" % (incoming_occurrence.language, exception_name, exception_package, exception_klass, exception_method, exception_line)
  location_hash = hashlib.sha1(location_salt).hexdigest()

  def bug_txn(key_name):
    bug = Bug.get_by_key_name(key_name)
    if bug is None:
      bug = Bug(key_name=key_name, product=product, exception_name=exception_name,
          exception_package=exception_package, exception_klass=exception_klass,
          exception_method=exception_method, exception_line=exception_line,
          max_severity=incoming_occurrence.severity, occurrence_count=incoming_occurrence.count,
          language=incoming_occurrence.language,
          first_occurrence_on=incoming_occurrence.date, last_occurrence_on=incoming_occurrence.date,
          roles=[incoming_occurrence.role], role_count=1,
          state=BUG_OPEN)
    else:
      bug.max_severity        = max(bug.max_severity, incoming_occurrence.severity)
      bug.occurrence_count   += incoming_occurrence.count
      bug.first_occurrence_on = min(bug.first_occurrence_on, incoming_occurrence.date)
      bug.last_occurrence_on  = max(bug.last_occurrence_on, incoming_occurrence.date)
      bug.roles               = list(set(bug.roles + [incoming_occurrence.role]))
      bug.role_count          = len(bug.roles)
    bug.put()
    return bug
  bug = db.run_in_transaction(bug_txn, Bug.key_name_for(product.key().id_or_name(), location_hash))

  def case_txn(key_name):
    case = Case.get_by_key_name(key_name)
    if case is None:
      case = Case(key_name=key_name, product=product, context=context, bug=bug,
        severity=incoming_occurrence.severity, language=incoming_occurrence.language, exceptions=incoming_occurrence.exceptions_json,
        occurrence_count=incoming_occurrence.count, first_occurrence_on=incoming_occurrence.date, last_occurrence_on=incoming_occurrence.date,
        roles=[incoming_occurrence.role])
    else:
      if case._bug is None: case.bug = bug # XXX temporary, remove me when migration is done
      case.occurrence_count   += incoming_occurrence.count
      case.first_occurrence_on = min(case.first_occurrence_on, incoming_occurrence.date)
      case.last_occurrence_on  = max(case.last_occurrence_on, incoming_occurrence.date)
      case.roles               = list(set(case.roles + [incoming_occurrence.role]))
    case.put()
    return case
  case = db.run_in_transaction(case_txn, Case.key_name_for(product.key(), incoming_occurrence.case_hash))

  def occurrence_txn(key_name):
    occurrence = Occurrence.get_by_key_name(key_name)
    if occurrence is None:
      occurrence = Occurrence(key_name=key_name, case=case, client=client, bug=bug, 
          date=incoming_occurrence.date, count=incoming_occurrence.count,
          role=incoming_occurrence.role, week=incoming_occurrence.week)
      if incoming_occurrence.exception_messages:
        occurrence.exception_messages = incoming_occurrence.exception_messages
      for k, v in incoming_occurrence.data.iteritems():
        setattr(occurrence, 'data_%s' % k, db.Text(unicode(v)))
      for k, v in incoming_occurrence.env.iteritems():
        setattr(occurrence, 'env_%s' % k, db.Text(unicode(v)))
    else:
      if occurrence._bug is None: occurrence.bug = bug # XXX temporary, remove me when migration is done
      occurrence.count += incoming_occurrence.count
    occurrence.put()
    return occurrence
  occurrence = db.run_in_transaction(occurrence_txn, Occurrence.key_name_for(case.key().id_or_name(), client.key().id_or_name(), incoming_occurrence.occurrence_hash))
  
  def week_txn(key_name):
    stat = BugWeekStat.get_by_key_name(key_name)
    if stat is None:
      stat = BugWeekStat(key_name=key_name, product=product, bug=bug, week=incoming_occurrence.week,
        count=incoming_occurrence.count, first=incoming_occurrence.date, last=incoming_occurrence.date)
    else:
      stat.count += incoming_occurrence.count
      stat.first  = min(stat.first, incoming_occurrence.date)
      stat.last   = max(stat.last, incoming_occurrence.date)
    stat.put()
  db.run_in_transaction(week_txn, BugWeekStat.key_name_for(bug.key(), incoming_occurrence.week))
  
  return bug, occurrence
  
def process_report(report):
  try:
    try:
      data = json.loads(report.data)
      incoming_occurrences = [ReportedOccurrence(item, report.product) for item in data]
    except ValueError, e:
      raise ApiError, e
    except KeyError, e:
      raise ApiError, e
      
    product = report.product
    client  = report.client
    
    occurrences = []
    bugs = []
    
    tuples = [process_incoming_occurrence(product, client, incoming_occurrence) for incoming_occurrence in incoming_occurrences]
    report.occurrences =          [occurrence.key() for bug, occurrence in tuples]
    bugs               = list(set([bug              for bug, occurrence in tuples]))
    
    bugs_to_email = [b for b in bugs if b.should_spam()]
    if bugs_to_email:
      emails = product.list_of_new_bug_notification_emails()
      if emails:
        for bug in bugs_to_email:
          send_email_notifications(bug, emails, product.account, product)

  except ApiError, e:
    report.error = "%s: %s" % (e.__class__.__name__, e.message)
    report.status = REPORT_ERROR
    report.put()
    return
  report.status = REPORT_OK
  report.put()

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
  
  def __init__(self, data, product):

    if 'date' in data:
      self.date = date(*(time.strptime(data['date'], '%Y-%m-%d')[0:3]))
    else:
      self.date = date.today()
    
    self.count = int(data.get('count', 1))
    
    mm = [e.get('message', '') for e in data['exceptions']]
    self.exception_messages = [db.Text(x) for x in mm if x]
    
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

    self.exceptions_json = repr(self.exceptions)

    case_salt = "%s|%s|%s|%s" % (self.severity, self.context_name, self.language, self.exceptions_json)
    self.case_hash = hashlib.sha1(case_salt).hexdigest()

    occurrence_salt = "%s|%s|%s|%s|%s|%s" % (self.case_hash, repr(self.exception_messages), repr(self.env), repr(self.data), self.date, self.role)
    self.occurrence_hash = hashlib.sha1(occurrence_salt).hexdigest()
    
    self.definitive_location = self._compute_definitive_location(product)
    self.week = date_to_week(self.date)
   
  def _compute_definitive_location(self, product):
    index = 0
    for exception in self.exceptions:
      locations = exception['locations']
      for location in locations:
        package_name, class_name, method_name, line = location['package'], location['klass'], location['method'], location['line']
        if product.is_interesting_package(package_name):
          return (index, exception['name'], package_name, class_name, method_name, line)
      index += 1
    raise StandardError, "No exception info recorded for this case"
