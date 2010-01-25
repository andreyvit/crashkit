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

from jinja2 import Template, Environment, FileSystemLoader
from crashkitserver import filters
jinja2_env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))))
for name in filters.__all__:
  jinja2_env.filters[name] = getattr(filters, name)
for k, v in jinja2_env.get_template('macros/macros.html').module.__dict__.iteritems():
  jinja2_env.globals[k] = v

from yoursway.web.handling import before_request, access_check, fetcher, StopRequest, NotFound, AccessDenied, YSHandler

@before_request
def with_user(self):
  self.user = users.get_current_user()
  if self.user:
    self.person = db.get(Person.key_for(self.user.email()))
    if not self.person:
      self.person = Person(key_name=Person.key_for(self.user.email()).name(), user=self.user)
      if users.is_current_user_admin():
        self.person.put()
  else:
    self.person = AnonymousPerson()
  
  self.user_is_admin = users.is_current_user_admin()
  self.signout_url   = users.create_logout_url('/')
  self.signin_url    = users.create_login_url(self.request.url)

@before_request
def with_flash(self):
  try:
    self._flash = Flash()
  except EOFError:
    # this is a workaround for an unknown problem when running live on Google App Engine
    class PseudoFlash:
      def __init__(self):
        self.msg = ''
    self._flash = PseudoFlash()
  self.flash_message = self._flash.msg


# CrashKitGAE
class BaseHandler(YSHandler, webapp.RequestHandler):
  
  @before_request
  def basic_init(self):
    self.now = datetime.now()
    self.validation_errors = False
    
  decorators = (with_flash,)
    
  def render_not_found_error_html(self, exception, debug_mode):
    self.render('404.html')
    
  def render_unknown_exception_error_html(self, exception, debug_mode):
    self.render('500.html')
    
  def render_bad_request_error_html(self, exception, debug_mode):
    self.render('400.html')
    
  def render_access_denied_error_html(self, exception, debug_mode):
    self.render('403.html')

  def flash(self, message):
    self._flash.msg = message
    
  def redirect_and_finish(self, url, flash=None):
    if flash:
      self.flash(flash)
    self.redirect(url)
    raise StopRequest
    
  def send_urlencoded_and_finish(self, **hash):
    self.response.out.write(urllib.urlencode(hash))
    raise StopRequest
    
  def blow(self, code, response, **data):
    self.error(code)
    data.update(response = response)
    self.response.out.write(urllib.urlencode(data))
    raise StopRequest
    
  def render(self, *path_components):
    template = jinja2_env.get_template(os.path.join(*path_components))
    self.response.out.write(template.render(self.__dict__))
    raise StopRequest
    
  def render_and_finish(self, *path_components):
    self.render(*path_components)
    raise StopRequest
    
  def access_denied(self, message = "Sorry, you do not have access to this page.",
        attemp_login = True):
    if attemp_login and self.user == None and self.request.method == 'GET':
      self.redirect_and_finish(users.create_login_url(self.request.uri))
    self.die(403, 'access_denied.html', message=message)
    
  def force_login(self):
    self.redirect_and_finish(users.create_login_url(self.request.uri))

  def not_found(self, message = None):
    self.die(404, 'not_found.html', message=message)

  def invalid_request(self, message = None):
    self.die(400, 'invalid_request.html', message=message)
    
  def die(self, code, template, message = None):
    if message:
      logging.warning("%d: %s" % (code, message))
    self.error(code)
    self.data.update(message = message)
    self.render_and_finish('errors', template)

class WebHandler(BaseHandler):
  
  decorators = (with_flash, with_user)


class ApiHandler(BaseHandler):
  
  decorators = ()
