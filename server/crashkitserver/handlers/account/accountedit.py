# -*- coding: utf-8
from google.appengine.api import users, memcache, mail
from google.appengine.ext import db

from crashkitserver.handlers.common import WebHandler
from crashkitserver.handlers.accesschecks import requires_account_admin, requires_signup_priv
from crashkitserver.handlers.fetchers import with_account, with_new_account

from models import Account, Person, AccountAccess, ProductAccess, LimitedBetaCandidate
from yoursway.utils.stringutil import random_string
from wtforms import Form, TextField, validators

class AccountForm(Form):
  permalink = TextField('Permalink', [validators.Length(min=4, max=100), validators.Regexp('^[a-zA-Z0-9-]*$', message="Only letters, numbers and dashes, please."), validators.Regexp('^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$', message="Must start with a letter, cannot end with a dash.")])
  name      = TextField('Name', [validators.Length(min=1)])

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
  
class AccountPeopleHandler(WebHandler):

  @with_account
  @requires_account_admin
  def get(self):
    self.fetch()
    self.render_screen_and_finish()

  @with_account
  @requires_account_admin
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
          self.new_person_email = new_person_email
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
    
    for person in self.people:
      for product in self.products:
        if not product.key() in person.product_authorization:
          person.product_authorization[product.key()] = ProductAccess(key_name=ProductAccess.key_for(person.key(), product.key()).name(),
            person=person, product=product, level=(ACCESS_READ if product.public_access else ACCESS_NONE))
    
  def render_screen_and_finish(self):
    self.tabid = 'people-tab'
    self.render_and_finish('account_people.html')

class AccountSettingsHandler(WebHandler):

  @with_account
  @requires_account_admin
  def get(self):
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.tabid = 'account-settings-tab'
    self.render_and_finish('account_settings.html')

  @with_account
  @requires_account_admin
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


class SignupHandler(WebHandler):

  @with_new_account
  def get(self, invitation_code):
    self.invitation_code = invitation_code
    self.tabid = 'account-settings-tab'
    if not users.is_current_user_admin():
      if invitation_code == None or len(invitation_code.strip()) == 0:
        self.render_and_finish('account_signup_nocode.html')
      candidate = LimitedBetaCandidate.all().filter('invitation_code', invitation_code).get()
      if candidate == None:
        self.render_and_finish('account_signup_badcode.html')
    if not self.user:
      self.render_and_finish('account_signup_googlenotice.html')

    self.account_form = AccountForm()
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.tabid = 'account-settings-tab'
    self.render_and_finish('account_settings.html')

  @with_new_account
  @requires_signup_priv
  def post(self, invitation_code):
    if not users.is_current_user_admin():
      candidate = LimitedBetaCandidate.all().filter('invitation_code', invitation_code).get()
      if candidate == None:
        self.redirect_and_finish('/signup/%s' % invitation_code)
        
    self.account_form = AccountForm(self.request.POST)
    if self.account_form.validate():
      existing_account = Account.all().filter('permalink', self.account.permalink).get()
      if existing_account:
        self.account_form.permalink.errors.append("This name is already taken.")
      else:
        self.account_form.populate_obj(self.account)
        self.account.put()
        if not self.person.is_saved():
          self.person.put()
        self.account_access = AccountAccess(key_name=AccountAccess.key_for(self.person.key(), self.account.key()).name(),
            person=self.person, account=self.account, admin=True)
        self.account_access.put()
        self.redirect_and_finish(u'/%s/products/new/' % self.account.permalink,
          flash = u"Your account has been created. You can add your first product now.")
      
    self.render_screen_and_finish()


url_mapping = (
  ('/signup/([a-zA-Z0-9]*)', SignupHandler),
  ('/([a-zA-Z0-9._-]+)/people/', AccountPeopleHandler),
  ('/([a-zA-Z0-9._-]+)/settings/', AccountSettingsHandler),
)
