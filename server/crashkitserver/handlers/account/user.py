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

from controllers.base import *

class ProfileHandler(BaseHandler):

  @prolog(fetch=['account_authorizations'], check=[])
  def get(self):
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.data.update(tabid = 'profile-tab', account_authorizations=self.account_authorizations)
    self.render_and_finish('user_profile.html')

  # @prolog(fetch=['account', 'or_create_product'], check=['is_product_admin_allowed'])
  # def post(self):
  #   is_saved = self.product.is_saved()
  #   self.product.unique_name = self.valid_string('unique_name')
  #   self.product.friendly_name = self.valid_string('friendly_name')
  #   self.product.public_access = self.valid_bool('public_access')
  #   self.product.bug_tracker = self.valid_string('bug_tracker', required=False)
  #   self.product.bug_tracker_url = self.valid_string('bug_tracker_url', required=(self.product.bug_tracker != None))
  #   self.product.new_bug_notification_emails = self.valid_string('new_bug_notification_emails', required=False, use_none=False)
  #   if self.product.is_saved():
  #     self.product.uninteresting_packages = self.valid_string('uninteresting_packages')
  #   if not self.is_valid():
  #     self.render_screen_and_finish()
  #   self.product.put()
  #   if is_saved:
  #     self.redirect_and_finish(u'%s/products/%s/settings' % (self.account_path, self.product.unique_name),
  #       flash = u"“%s” has been saved." % self.product.friendly_name)
  #   else:
  #     if not self.person.is_saved():
  #       self.person.put()
  #     self.product_access = ProductAccess(key_name=ProductAccess.key_for(self.person.key(), self.product.key()).name(),
  #         product=self.product, person=self.person, level=ACCESS_ADMIN)
  #     self.product_access.put()
  #     self.redirect_and_finish(u'%s/products/%s/all' % (self.account_path, self.product.unique_name),
  #       flash = u"“%s” has been created." % self.product.friendly_name)

url_mapping = (
  ('/profile/', ProfileHandler),
)
