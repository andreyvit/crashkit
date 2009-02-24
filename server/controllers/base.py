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

template_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
template.register_template_library('myfilters')


class FinishRequest(Exception):
  pass

class prolog(object):
  def __init__(decor, fetch = [], config_needed = True):
    decor.config_needed = config_needed
    decor.fetch = fetch
    pass

  def __call__(decor, original_func):
    def decoration(self, *args):
      try:
        args = list(args)
        for func in decor.fetch:
          func = getattr(self, 'fetch_%s' % func)
          try:
            func()
          except TypeError, e:
            arg = args[0]
            del args[0]
            func(arg)
        return original_func(self, *args)
      except FinishRequest:
        pass
    decoration.__name__ = original_func.__name__
    decoration.__dict__ = original_func.__dict__
    decoration.__doc__  = original_func.__doc__
    return decoration

class BaseHandler(webapp.RequestHandler):
  def __init__(self):
    self.now = datetime.now()
    self.data = dict(now = self.now)
    
  def redirect_and_finish(self, url, flash = None):
    self.redirect(url)
    raise FinishRequest
    
  def send_urlencoded_and_finish(self, **hash):
    self.response.out.write(urllib.urlencode(hash))
    raise FinishRequest
    
  def blow(self, code, response, **data):
    self.error(code)
    data.update(response = response)
    self.response.out.write(urllib.urlencode(data))
    raise FinishRequest
    
  def render_and_finish(self, *path_components):
    self.response.out.write(template.render(os.path.join(template_path, *path_components), self.data))
    raise FinishRequest
    
  def access_denied(self, message = None, attemp_login = True):
    if attemp_login and self.user == None and self.request.method == 'GET':
      self.redirect_and_finish(users.create_login_url(self.request.uri))
    self.die(403, 'access_denied.html', message=message)

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
    
  def fetch_account(self):
    self.account = Account.get_or_insert(self.request.host, host = self.request.host)
    self.data.update(account=self.account)
    
  def fetch_product(self, product_name):
    self.product = self.account.products.filter('unique_name =', product_name).get()
    if self.product == None:
      self.not_found("Product not found")
    self.data.update(product=self.product)

  def fetch_bug(self, bug_name):
    self.bug = Bug.get_by_key_name(bug_name)
    if self.bug == None or self.bug.product.key() != self.product.key():
      self.not_found("Bug not found")
    self.data.update(bug=self.bug)
    
  def fetch_client(self, client_id):
    self.client = Client.get_by_id(int(client_id))
    if self.client == None:
      logging.warn('Client ID requested but not found: "%s"' % client_id)
      self.blow(403, 'invalid-client-id')
    self.data.update(client=self.client)
  
  def fetch_client_cookie(self, client_cookie):
    if client_cookie != self.client.cookie:
      logging.warn('Client ID cookie invalid: "%s" / "%s"' % (client_id, client_cookie))
      self.blow(403, 'invalid-client-id')
