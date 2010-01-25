# -*- coding: utf-8
from datetime import datetime, timedelta
import time
import logging
import wsgiref.handlers
import os
import string
import urllib
import sets
import re
from random import Random
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson as json
from models import *
from appengine_utilities.flash import Flash
from crashkit import initialize_crashkit, CrassKitGAE

from yoursway.web.handling import fetcher

template_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
template.register_template_library('myfilters')

initialize_crashkit('ys', 'crashkit', app_dirs=[os.path.join(os.path.dirname(__file__), '..')])


      
  def invalid(self, key, message):
    error_key = '%s_error' % key
    if not error_key in self.data:
      self.data.update(**{error_key: message})
    self.validation_errors = True
    return None
    
  DEFAULT_REQUIRED_MESSAGE = "Required."
    
  def is_valid(self, key = None):
    if key:
      return not (key + '_error') in self.data
    return not self.validation_errors
  
  def valid_string(self, key, required=True, use_none=True, min_len=None, max_len=None,
        required_message = DEFAULT_REQUIRED_MESSAGE,
        min_len_message = "Please enter at least %(min)d characters.",
        max_len_message = "Cannot be longer that %(max)d characters."):
    value = self.request.get(key)
    data = dict(value=value, key=key, min=min_len, max=max_len, len=(0 if value==None else len(value)))
    if value != None:
      value = value.strip()
    if value == None or len(value) == 0:
      if required:
        self.invalid(key, required_message % data)
        return value
      else:
        value = None if use_none else ""
    if min_len and len(value) < min_len:
      self.invalid(key, min_len_message % data)
      return value
    if max_len and len(value) > max_len:
      self.invalid(key, max_len_message % data)
      return value
    return value
  
  def valid_int(self, key, required=True, min_value=None, max_value=None,
        required_message = DEFAULT_REQUIRED_MESSAGE,
        not_a_number_message = "Must be a number.",
        min_value_message = "Cannot be less than %(minval)d.",
        max_value_message = "Cannot be greater than %(maxval)d."):
    s = self.valid_string(key, required=required, use_none=True, required_message=required_message)
    if not self.is_valid(key):
      return s
    if not re.match('^-?[0-9]+$', s):
      return self.invalid(key, not_a_number_message)
    i = int(s)
    data = dict(value=i, key=key, min_value=min_value, max_value=max_value)
    if min_value != None and i < min_value:
      return self.invalid(key, min_value_message)
    if max_value != None and i > max_value:
      return self.invalid(key, max_value_message)
    return i
  
  def valid_bool(self, key):
    s = self.request.get(key)
    return s == '1' or s == 'yes' or s == 'on' or s == 'True'
    
  def check_is_server_management_allowed(self):
    if not users.is_current_user_admin():
      self.access_denied("You cannot access server-wide management unless you are a developer of YourSway CrashKit.")
      
  def check_is_account_admin_allowed(self):
    if not self.account_access.is_admin_allowed():
      self.access_denied("You need to be an administrator of the account to change its settings.")
      
  def check_is_managing_people_allowed(self):
    if not self.account_access.is_managing_people_allowed():
      self.access_denied("You need to be an administrator of the account to manage people & permissions.")
      
  def check_is_product_admin_allowed(self):
    if self.product_access:
      if not self.product_access.is_admin_allowed():
        self.access_denied("You need to be an administrator of the account to change project settings.")
    else:
      if not self.account_access.is_admin_allowed():
        self.access_denied("You need to be an administrator of the account to add a project.")
      
  def check_is_product_write_allowed(self):
    if not self.product_access.is_write_allowed():
      self.access_denied("You need to have a write access to %s." % self.product.friendly_name)
      
  
  def requires_signup_priv(self):
    if not self.person.is_signup_allowed():
      self.access_denied("You have not been invited into our beta program yet. Sorry, buddy.")

