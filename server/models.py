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
from commons import *
  
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

class LimitedBetaCandidate(db.Model):
  email           = db.StringProperty(required=True)
  tech            = db.StringProperty(required=True)
  invitation_code = db.StringProperty(default=None)
  rejected        = db.BooleanProperty(default=False)
  created_at      = db.DateTimeProperty(auto_now_add = True)

class Account(db.Model):
  name = db.TextProperty(default=None)
  permalink = db.StringProperty(default=None)
  host = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
    
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
  
  new_bug_notification_emails = db.TextProperty(default='')
  
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
  
  last_email_on = db.DateProperty(default=None)
  
  def should_spam(self):
    if self.last_email_on == None:
      return True
    if (self.last_occurrence_on - self.last_email_on).days > 0:
      return True
    return False
    
  def describe_for_email(self, product_path):
    return u"""
Bug:        %(url)s
Exception:  %(exception_name)s
In:         %(exception_package)s.%(exception_klass)s.%(exception_method)s:%(exception_line)s
Occurred:   %(occurrence_count)s time(s)
Last time:  %(last_occurrence_on)s
""" % dict(url='%s/bugs/%s' % (product_path, self.key()),
  exception_name=self.exception_name, exception_package=self.exception_package,
  exception_klass=self.exception_klass, exception_method=self.exception_method,
  exception_line=self.exception_line, occurrence_count=self.occurrence_count,
  last_occurrence_on=self.last_occurrence_on)
  
    
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
    
class Person(db.Model):
  user = db.UserProperty(required=True)
  
  def account_access_for(self, account):
    if not self.is_saved():
      return AnonymousAccountAccess(account)
    account_access = db.get(AccountAccess.key_for(self.key(), account.key()))
    if not account_access:
      account_access = AccountAccess(key_name=AccountAccess.key_for(self.key(), account.key()).name(), account=account, person=self)
    return account_access
    
  def is_signup_allowed(self):
    return True
  
  @staticmethod
  def key_for(email):
    return db.Key.from_path('Person', 'u' + email)

class AnonymousPerson(object):
  
  def account_access_for(self, account):
    return AnonymousAccountAccess(account)
    
  def is_signup_allowed(self):
    return False
  
    
class AccountAccess(db.Model):
  account = db.ReferenceProperty(Account, required=True, collection_name='people_authorizations')
  person = db.ReferenceProperty(Person, required=True, collection_name='account_authorizations')
  admin = db.BooleanProperty(default=False)
    
  def product_access_for(self, product):
    if self.admin:
      return FullProductAccess()
    access = db.get(ProductAccess.key_for(self.person.key(), product.key()))
    if not access:
      access = PublicProductAccess(product)
    return access

  def is_managing_people_allowed(self):
    return self.admin
    
  def is_admin_allowed(self):
    return self.admin
  
  @staticmethod
  def key_for(person_key, account_key):
    return db.Key.from_path('AccountAccess', 'a%sp%s' % (account_key.id_or_name(), person_key.id_or_name()))
    

class AnonymousAccountAccess(db.Model):
  def __init__(self, account):
    self.admin = False
  def product_access_for(self, product):
    return PublicProductAccess(product)
  def is_managing_people_allowed(self):
    return False
  def is_admin_allowed(self):
    return False
    

ACCESS_NONE = 0
ACCESS_READ = 1
ACCESS_WRITE = 2
ACCESS_ADMIN = 3

class ProductAccess(db.Model):
  person = db.ReferenceProperty(Person, required=True)
  product = db.ReferenceProperty(Product, required=True)
  level = db.IntegerProperty(choices=[ACCESS_NONE,ACCESS_READ,ACCESS_WRITE,ACCESS_ADMIN])
    
  def is_listing_allowed(self):
    return self.level > ACCESS_NONE
  def is_viewing_allowed(self):
    return self.product.public_access or self.level > ACCESS_NONE
  def is_write_allowed(self):
    return self.level >= ACCESS_WRITE
  def is_admin_allowed(self):
    return self.level >= ACCESS_ADMIN
  
  @staticmethod
  def key_for(person_key, product_key):
    return db.Key.from_path('ProductAccess', 'p%sp%s' % (person_key.id_or_name(), product_key.id_or_name()))

class PublicProductAccess(object):
  
  def __init__(self, product):
    self.product = product
    
  def is_listing_allowed(self):
    return self.product.public_access
  def is_viewing_allowed(self):
    return self.product.public_access
  def is_write_allowed(self):
    return False
  def is_admin_allowed(self):
    return False

class FullProductAccess(object):
  
  def is_listing_allowed(self):
    return True
  def is_viewing_allowed(self):
    return True
  def is_write_allowed(self):
    return True
  def is_admin_allowed(self):
    return True
