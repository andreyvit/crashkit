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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson as json
from models import *
from processor import process_report, process_case
from commons import *

from controllers.base import *

# Show: New | All      Most Recent | Most Occurring

def create_person_txn(email):
  key = Person.key_for(email)
  p = db.get(key)
  if not p:
    p = Person(key_name=key.name(), user=users.User(email))
    p.put()

def update_person_account_access_txn(person_key, account_key, admin):
  key = AccountAccess.key_for(person_key, account_key)
  a = db.get(key)
  if not a:
    a = AccountAccess(key_name=key.name(), person=person_key, account=account_key)
  a.admin = admin
  a.put()

def update_person_product_access_txn(person_key, product_key, level):
  key = ProductAccess.key_for(person_key, product_key)
  a = db.get(key)
  if not a:
    a = ProductAccess(key_name=key.name(), person=person_key, product=product_key)
  a.level = level
  a.put()
  
class AccountPeopleHandler(BaseHandler):

  @prolog(fetch=['account'], check = ['is_managing_people_allowed'])
  def get(self):
    self.fetch()
    self.render_screen_and_finish()

  @prolog(fetch=['account'], check = ['is_managing_people_allowed'])
  def post(self):
    self.fetch()
    
    for person in self.people:
      if self.request.get(u'person_%s_remove' % str(person.key())):
        for auth in person.product_authorization.values():
          auth.delete()
        person.account_access.delete()
        person.delete()
        self.redirect_and_finish(u'%s/people/' % self.account_path, flash = u"%s removed." % (person.user.email()))
    
    if self.request.get('new'):
      txns = []
      new_person_email = self.valid_string(u'new_person_email', required=False)
      if new_person_email != None:
        txns.append((create_person_txn, new_person_email))
        person_key = Person.key_for(new_person_email)
        
        admin = self.valid_bool(u'new_person_admin')
        txns.append((update_person_account_access_txn, person_key, self.account.key(), admin))
        
        for product in self.products:
          level = self.valid_int(u'new_person_%s_level' % (product.key()))
          txns.append((update_person_product_access_txn, person_key , product.key(), level))
          
        if self.is_valid():
          for txn in txns:
            db.run_in_transaction(*txn)
          self.redirect_and_finish(u'%s/people/' % self.account_path, flash = u"%s has been created." % new_person_email)
        else:
          self.data.update(new_person_email=new_person_email)
          self.render_screen_and_finish()
    else:      
      txns = []
      for person in self.people:
        admin = self.valid_bool(u'person_%s_admin' % person.key())
        txns.append((update_person_account_access_txn, person.key(), self.account.key(), admin))
        for product in self.products:
          level = self.valid_int(u'person_%s_%s_level' % (person.key(), product.key()))
          txns.append((update_person_product_access_txn, person.key(), product.key(), level))
    
      if self.is_valid():
        for txn in txns:
          db.run_in_transaction(*txn)
        self.redirect_and_finish(u'%s/people/' % self.account_path, flash = u"Permission settings have been saved.")
      else:
        self.render_screen_and_finish()
    
  def fetch(self):
    self.people_authorizations = self.account.people_authorizations.fetch(100)
    self.people = map(lambda a: a.person, self.people_authorizations)
    for a in self.people_authorizations:
      a.person.account_access = a
    self.people_project_authorizations = ProductAccess.all().filter('person IN', self.people).fetch(1000)
    auth_list_by_person_key = group(lambda a: a.person.key(), self.people_project_authorizations)
    for person in self.people:
      try:
        person.product_authorization = index(lambda a: a.product.key(), auth_list_by_person_key[person.key()])
      except KeyError:
        person.product_authorization = {}
      
    self.products = self.account.products.fetch(100)
    
  def render_screen_and_finish(self):
    self.data.update(tabid = 'people-tab', people=self.people, products=self.products)
    self.render_and_finish('account_people.html')

def validate_account(self):
  if not re.match('^[a-zA-Z0-9-]*$', self.account.permalink):
    self.invalid('permalink', "Only letters, numbers and dashes, please.")
  if len(self.account.permalink) < 4 and not users.is_current_user_admin():
    self.invalid('permalink', "Please enter at least 4 characters.")
  if not re.match('^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$', self.account.permalink):
    self.invalid('permalink', "Must start with a letter, cannot end with a dash.")


class AccountSettingsHandler(BaseHandler):

  @prolog(fetch=['account'], check=['is_account_admin_allowed'])
  def get(self):
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.data.update(tabid = 'account-settings-tab')
    self.render_and_finish('account_settings.html')

  @prolog(fetch=['account'], check=['is_account_admin_allowed'])
  def post(self):
    self.account.permalink = self.valid_string('permalink')
    self.account.name = self.valid_string('name')
    
    validate_account(self)
    existing_account = Account.all().filter('permalink', self.account.permalink).get()
    if existing_account and existing_account.key().id_or_name() != self.account.key().id_or_name():
      self.invalid('permalink', "This name is already taken.")
    
    if not self.is_valid():
      self.render_screen_and_finish()
    self.account.put()
    self.redirect_and_finish(u'/%s/settings/' % self.account.permalink,
      flash = u"“%s” settings have been saved." % self.account.name)


class SignupHandler(BaseHandler):

  @prolog(fetch=['new_account'])
  def get(self, invitation_code):
    self.data.update(invitation_code=invitation_code, tabid='account-settings-tab')
    if not users.is_current_user_admin():
      if invitation_code == None or len(invitation_code.strip()) == 0:
        self.render_and_finish('account_signup_nocode.html')
      candidate = LimitedBetaCandidate.all().filter('invitation_code', invitation_code).get()
      if candidate == None:
        self.render_and_finish('account_signup_badcode.html')
    if not self.user:
      self.render_and_finish('account_signup_googlenotice.html')
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.data.update(tabid = 'account-settings-tab')
    self.render_and_finish('account_settings.html')

  @prolog(fetch=['new_account'], check=['is_signup_allowed'])
  def post(self, invitation_code):
    if not users.is_current_user_admin():
      candidate = LimitedBetaCandidate.all().filter('invitation_code', invitation_code).get()
      if candidate == None:
        self.redirect_and_finish('/signup/%s' % invitation_code)
    
    self.account.permalink = self.valid_string('permalink')
    self.account.name = self.valid_string('name')
    
    validate_account(self)
    existing_account = Account.all().filter('permalink', self.account.permalink).get()
    if existing_account:
      self.invalid('permalink', "This name is already taken.")
      
    if not self.is_valid():
      self.render_screen_and_finish()
    self.account.put()
    self.account_access = AccountAccess(key_name=AccountAccess.key_for(self.person.key(), self.account.key()).name(),
        person=self.person, account=self.account, admin=True)
    self.account_access.put()
    self.redirect_and_finish(u'/%s/products/new/' % self.account.permalink,
      flash = u"Your account has been created. You can add your first product now." % self.account.name)
    # else:
    #   if not self.person.is_saved():
    #     self.person.put()
    #   self.product_access = ProductAccess(key_name=ProductAccess.key_for(self.person.key(), self.product.key()).name(),
    #       product=self.product, person=self.person, level=ACCESS_ADMIN)
    #   self.product_access.put()
    #   self.redirect_and_finish(u'/%s/%s/all' % (self.account_path, self.product.permalink),
    #     flash = u"“%s” has been created." % self.product.name)
