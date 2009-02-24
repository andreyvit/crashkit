# -*- coding: utf-8
from datetime import datetime, timedelta
import time
import logging
import wsgiref.handlers
import os
import string
import urllib
import sets
from random import Random
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson as json

def random_string(len = 12, chars = string.letters+string.digits):
  return ''.join(Random().sample(chars, 12))
  
def flatten(l, ltypes=(list, tuple)):
  ltype = type(l)
  l = list(l)
  i = 0
  while i < len(l):
    while isinstance(l[i], ltypes):
      if not l[i]:
        l.pop(i)
        i -= 1
        break
      else:
        l[i:i + 1] = l[i]
    i += 1
  return ltype(l)

# models

def transaction(method):
  def decorate(*args, **kwds):
    return db.run_in_transaction(method, *args, **kwds)
  return decorate
  
class Account(db.Model):
  host = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
  
  def name(self):
    return self.host
    
BUG_TRACKERS = (
  ('lighthouse', dict(name='Lighthouse', ticket='%s/tickets/%s')),
  ('redmine', dict(name='Redmine', ticket='%s/issues/show/%s')),
  ('trac', dict(name='Trac', ticket='%s/ticket/%s')),
)
BUG_TRACKERS_DICT = dict(BUG_TRACKERS)

def match_package(pattern, item):
  return (item + '.').startswith(pattern + '.')

class Product(db.Model):
  account = db.ReferenceProperty(Account, collection_name = 'products')
  unique_name = db.StringProperty()
  friendly_name = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
  
  bug_tracker     = db.StringProperty()
  bug_tracker_url = db.StringProperty()
  
  public_access = db.BooleanProperty()
  
  uninteresting_packages = db.TextProperty(default="java,javax,sun,org.eclipse,com.yoursway.utils.bugs")
  
  def is_interesting_package(self, name):
    for uninteresting_package in map(lambda s: s.strip(), self.uninteresting_packages.split(',')):
      if uninteresting_package[0] == '!':
        if match_package(uninteresting_package[1:], name):
          return True
      else:
        if match_package(uninteresting_package, name):
          return False
    return True
  
  def bug_tracker_name(self):
    if self.bug_tracker in BUG_TRACKERS_DICT:
      return BUG_TRACKERS_DICT[self.bug_tracker]['name']
    return 'Bug tracker'
      
  def bug_tracker_autolinking(self):
    return self.bug_tracker in BUG_TRACKERS_DICT
    
  def bug_tracker_ticket_url(self, ticket_id):
    if self.bug_tracker in BUG_TRACKERS_DICT:
      url = self.bug_tracker_url
      if url[-1] == '/':
        url = url[0:-1]
      if not url.startswith('http'):
        url = "http://" + url

      return BUG_TRACKERS_DICT[self.bug_tracker]['ticket'] % (url, ticket_id)
    if self.bug_tracker == 'other':
      return self.bug_tracker_url.replace('%s', ticket_id)
    return u''
  
class Client(db.Model):
  product = db.ReferenceProperty(Product, collection_name = 'clients')
  cookie = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
  last_bug_reported_at = db.DateTimeProperty()
  remote_ips = db.StringListProperty()

REPORT_NEW = 0
REPORT_OK = 1
REPORT_ERROR = 2
class Report(db.Expando):
  product = db.ReferenceProperty(Product, required=True, collection_name='reports')
  client  = db.ReferenceProperty(Client,  required=True, collection_name='reports')
  occurrences = db.ListProperty(db.Key)
  
  created_at = db.DateTimeProperty(auto_now_add = True)
  remote_ip = db.StringProperty(required=True)
  data = db.TextProperty(required=True)
  
  status = db.IntegerProperty(default = 0, choices=[0,1,2])
  error = db.TextProperty()
  
class Ticket(db.Model):
  product = db.ReferenceProperty(Product, required=True, collection_name='tickets')
  name = db.StringProperty(required=True)
  created_at = db.DateTimeProperty(auto_now_add = True)
  
  @staticmethod
  def key_name_for(product_name_or_id, name):
    return 'P%sT%s' % (product_name_or_id, name)

class Context(db.Model):
  product = db.ReferenceProperty(Product, required=True, collection_name = 'contexts')
  created_at = db.DateTimeProperty(auto_now_add = True)
  name = db.TextProperty(required=True)
  
  @staticmethod
  def key_name_for(product, name):
    return u'p-%s|c-%s' % (product.id_or_name(), name)
    
class Bug(db.Model):
  product = db.ReferenceProperty(Product, required=True, collection_name='bugs')
  ticket  = db.ReferenceProperty(Ticket, collection_name = "bugs")
  # name    = db.StringProperty(required=True)
  
  @staticmethod
  def key_name_for(product_id, location_hash):
    return 'P%s-L%s' % (product_id, location_hash)
  
  created_at = db.DateTimeProperty(auto_now_add = True)

  exception_name    = db.StringProperty(required=True)
  exception_package = db.StringProperty(required=True)
  exception_klass   = db.StringProperty(required=True)
  exception_method  = db.StringProperty(required=True)
  exception_line    = db.IntegerProperty(required=True)
  
  max_severity        = db.IntegerProperty(required=True)
  occurrence_count    = db.IntegerProperty(required=True)
  first_occurrence_on = db.DateProperty(required=True)
  last_occurrence_on  = db.DateProperty(required=True)
  roles               = db.StringListProperty()
  
    
class Case(db.Model):
  product = db.ReferenceProperty(Product, required=True, collection_name='cases')
  context = db.ReferenceProperty(Context, required=True, collection_name='cases')
  severity = db.IntegerProperty(required=True)
  
  bug    = db.ReferenceProperty(Bug, default=None, collection_name='cases')
  
  exceptions = db.TextProperty(required=True)
  
  created_at = db.DateTimeProperty(auto_now_add = True)
  
  occurrence_count = db.IntegerProperty(required=True)
  first_occurrence_on = db.DateProperty(required=True)
  last_occurrence_on = db.DateProperty(required=True)
  roles = db.StringListProperty()
  
  # exception_name    = db.StringProperty()
  # exception_package = db.StringProperty(required=True)
  # exception_klass   = db.StringProperty(required=True)
  # exception_method  = db.StringProperty(required=True)
  # exception_line    = db.IntegerProperty(required=True)
  
  @staticmethod
  def key_name_for(product, case_hash):
    return 'P%s-C%s' % (product.id_or_name(), case_hash)
    
  def exceptions_list(self):
    return eval(self.exceptions)
  
  def definitive_location(self, product):
    exceptions = eval(self.exceptions)
    index = 0
    for exception in exceptions:
      locations = exception['locations']
      for location in locations:
        package_name, class_name, method_name, line = location['package'], location['klass'], location['method'], location['line']
        if product.is_interesting_package(package_name):
          return (index, exception['name'], package_name, class_name, method_name, line)
      index += 1
    raise StandardError, "No exception info recorded for this case"
  #   
  # def exception_name(self):
  #   return self.definitive_location()[1]
  #   
  # def exception_package(self):
  #   return self.definitive_location()[2]
  #   
  # def exception_location(self):
  #   return '%s.%s' % (self.definitive_location()[3], self.definitive_location()[4])
  #   
  # def exception_klass(self):
  #   return self.definitive_location()[3]
  #   
  # def exception_method(self):
  #   return self.definitive_location()[4]
  #   
  # def exception_line(self):
  #   return self.definitive_location()[5]
    
  def bug_name(self):
    if self.severity == 1:
      return 'Bug'
    if self.severity == 2:
      return 'Major Bug'
    return 'Unknown Bug'
  
  def exception_names_as_string(self):
    return ", ".join([ e[e.rfind('.')+1:len(e)] for e in self.exception_names])

class Occurrence(db.Expando):
  case = db.ReferenceProperty(Case, collection_name = 'occurrences')
  client = db.ReferenceProperty(Client, collection_name = 'occurrences')
  created_at = db.DateTimeProperty(auto_now_add = True)
  
  exception_messages = db.TextProperty(required=True)
  date = db.DateProperty(required=True)
  count = db.IntegerProperty()
  role = db.StringProperty(required=True, default='customer')
    
  @staticmethod
  def key_name_for(case_key_name, client_key_name, occurrence_hash):
    return 'C%s-CL%s-O%s' % (case_key_name, client_key_name, occurrence_hash)

  # data_*
  # env_*
  
