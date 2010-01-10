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
from google.appengine.api import mail
from django.utils import simplejson as json
from models import *

from controllers.base import *

class StatusHandler(BaseHandler):
  
  @prolog()
  def get(self):
    queued_reports = Report.all().filter('status', 0).count()
    self.data.update(queued=queued_reports)
    self.render_and_finish('system_status.html')
