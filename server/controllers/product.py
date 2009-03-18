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

from controllers.base import *

# Show: New | All      Most Recent | Most Occurring

class ProductSettingsHandler(BaseHandler):

  @prolog(fetch=['account', 'or_create_product'], check=['is_product_admin_allowed'])
  def get(self):
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.data.update(tabid = 'product-tab', bug_trackers=BUG_TRACKERS)
    self.render_and_finish('product_settings.html')

  @prolog(fetch=['account', 'or_create_product'], check=['is_product_admin_allowed'])
  def post(self):
    is_saved = self.product.is_saved()
    self.product.unique_name = self.valid_string('unique_name')
    self.product.friendly_name = self.valid_string('friendly_name')
    self.product.public_access = self.valid_bool('public_access')
    self.product.bug_tracker = self.valid_string('bug_tracker', required=False)
    self.product.bug_tracker_url = self.valid_string('bug_tracker_url', required=(self.product.bug_tracker != None))
    self.product.new_bug_notification_emails = self.valid_string('new_bug_notification_emails', required=False, use_none=False)
    if self.product.is_saved():
      self.product.uninteresting_packages = self.valid_string('uninteresting_packages')
      
    if not re.match('^[a-zA-Z0-9-]*$', self.product.unique_name):
      self.invalid('unique_name', "Only letters, numbers and dashes, please.")
    if len(self.product.unique_name) < 4 and not users.is_current_user_admin():
      self.invalid('unique_name', "Please enter at least 4 characters.")
    if not re.match('^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$', self.product.unique_name):
      self.invalid('unique_name', "Must start with a letter, cannot end with a dash.")
    existing = self.account.products.filter('unique_name', self.product.unique_name).get()
    if existing and existing.key().id_or_name() != self.product.key().id_or_name():
      self.invalid('unique_name', "This name is already in use by another product in your account.")
      
    if not self.is_valid():
      self.render_screen_and_finish()
    self.product.put()
    if is_saved:
      self.redirect_and_finish(u'%s/products/%s/settings' % (self.account_path, self.product.unique_name),
        flash = u"“%s” has been saved." % self.product.friendly_name)
    else:
      if not self.person.is_saved():
        self.person.put()
      self.product_access = ProductAccess(key_name=ProductAccess.key_for(self.person.key(), self.product.key()).name(),
          product=self.product, person=self.person, level=ACCESS_ADMIN)
      self.product_access.put()
      self.redirect_and_finish(u'%s/products/%s/help/integration' % (self.account_path, self.product.unique_name),
        flash = u"“%s” has been created." % self.product.friendly_name)

class ProductHelpHandler(BaseHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.data.update(tabid = 'product-help-tab')
    self.render_and_finish('product_integration_help.html')
