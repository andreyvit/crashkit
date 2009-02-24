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

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.render_screen_and_finish()
    
  def render_screen_and_finish(self):
    self.data.update(tabid = 'product-tab', product_path=".", bug_trackers=BUG_TRACKERS)
    self.render_and_finish('project', 'settings.html')

  @prolog(fetch=['account', 'product'])
  def post(self):
    self.product.unique_name = self.valid_string('unique_name')
    self.product.friendly_name = self.valid_string('friendly_name')
    self.product.public_access = self.valid_bool('public_access')
    self.product.bug_tracker = self.valid_string('bug_tracker', required=False)
    self.product.bug_tracker_url = self.valid_string('bug_tracker_url', required=(self.product.bug_tracker != None))
    if not self.is_valid():
      self.render_screen_and_finish()
    self.product.put()
    self.redirect_and_finish(u'/%s/settings' % self.product.unique_name,
      flash = u"“%s” has been saved." % self.product.friendly_name)
