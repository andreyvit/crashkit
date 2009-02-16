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

template_path = os.path.join(os.path.dirname(__file__), 'templates')
template.register_template_library('myfilters')

def random_string(len = 12, chars = string.letters+string.digits):
  return ''.join(Random().sample(chars, 12))
  
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
  
class Account(db.Model):
  host = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)

class Product(db.Model):
  account = db.ReferenceProperty(Account, collection_name = 'products')
  unique_name = db.StringProperty()
  friendly_name = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)

class Client(db.Model):
  product = db.ReferenceProperty(Product, collection_name = 'clients')
  cookie = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
  last_bug_reported_at = db.DateTimeProperty()
  
class Problem(db.Model):
  product = db.ReferenceProperty(Product, collection_name = 'problems')
  created_at = db.DateTimeProperty(auto_now_add = True)
  severity = db.StringProperty()
  exception_names = db.StringListProperty()
  stack_trace = db.TextProperty()
  user_message = db.TextProperty()
  developer_message = db.TextProperty()
  occurrence_count = db.IntegerProperty()
  first_occurrence_at = db.DateTimeProperty()
  last_occurrence_at = db.DateTimeProperty()
  
  def message(self):
    if self.developer_message and self.user_message:
      return "%s — “%s”" % (self.developer_message, self.user_message)
    if self.developer_message:
      return self.developer_message
    if self.user_message:
      return u"“%s”" % self.user_message
    return "(No details)"
  
  def exception_names_as_string(self):
    return ", ".join([ e[e.rfind('.')+1:len(e)] for e in self.exception_names])
  
class Occurrence(db.Expando):
  problem = db.ReferenceProperty(Problem, collection_name = 'occurrences')
  client = db.ReferenceProperty(Client, collection_name = 'occurrences')
  first_occurrence_at = db.DateTimeProperty()
  last_occurrence_at = db.DateTimeProperty()
  count = db.IntegerProperty()
  

# controllers

class FinishRequest(Exception):
  pass

class prolog(object):
  def __init__(decor, path_components = [], fetch = [], config_needed = True):
    decor.config_needed = config_needed
    decor.path_components = path_components
    decor.fetch = fetch
    pass

  def __call__(decor, original_func):
    def decoration(self, *args):
      try:
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
    
  def send_urlencoded_and_finish(self, hash = dict()):
    self.response.out.write(urllib.urlencode(hash))
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


class MainHandler(BaseHandler):

  @prolog()
  def get(self):
    self.response.out.write('Hello world!')

class CreateProductHandler(BaseHandler):

  @prolog()
  def get(self):
    account = Account.get_or_insert(self.request.host, host = self.request.host)
    
    product = Product.all().filter('unique_name =', self.request.get('unique_name')).get()
    if product == None:
      product = Product()
    product.account = account
    product.unique_name = self.request.get('unique_name')
    product.friendly_name = self.request.get('friendly_name')
    product.put()
      
    self.send_urlencoded_and_finish(dict(created = 1, host = self.request.host))

class ObtainClientIdHandler(BaseHandler):

  @prolog()
  def get(self, product_name):
    account = Account.get_or_insert(self.request.host, host = self.request.host)
    product = Product.all().filter('unique_name =', product_name).filter('account =', account).get()
    if product == None:
      self.not_found("Product not found")
      
    client = Client()
    client.product = product
    client.cookie = random_string()
    client.put()
    self.send_urlencoded_and_finish(dict(client_id = client.key().id(), client_cookie = client.cookie))

class BugListHandler(BaseHandler):

  @prolog()
  def get(self, product_name):
    account = Account.get_or_insert(self.request.host, host = self.request.host)
    product = Product.all().filter('unique_name =', product_name).filter('account =', account).get()
    if product == None:
      self.not_found("Product not found")
      
    problems = product.problems.order('-occurrence_count').fetch(100)
    self.data.update(account = account, product = product, problems = problems)
    self.render_and_finish('buglist.html')

class BugHandler(BaseHandler):

  @prolog()
  def get(self, product_name, problem_name):
    account = Account.get_or_insert(self.request.host, host = self.request.host)
    product = Product.all().filter('unique_name =', product_name).filter('account =', account).get()
    if product == None:
      self.not_found("Product not found")
    problem = Problem.get_by_key_name(problem_name)
    if problem == None or problem.product.key() != product.key():
      self.not_found("Bug report not found")
    
    occurrences = problem.occurrences.order('-count').fetch(100)
    clients = Client.get([o.client.key() for o in occurrences])

    common_map = dict()
    for key in sets.Set(flatten([ [k for k in o.dynamic_properties() if k.startswith('env_') or k.startswith('data_')] for o in occurrences ])):
      set = sets.Set([s for s in [getattr(o, key) for o in occurrences if hasattr(o, key)] if s != None and len(s) > 0])
      if len(set) > 0:
        common_map[key] = set
    if 'env_hash' in common_map:
      del common_map['env_hash']
    
    # data_keys contains all columns that differ across occurrences
    data_keys = list(sets.Set(flatten([ [k for k in o.dynamic_properties() if k in common_map and len(common_map[k])>1] for o in occurrences ])))
    data_keys.sort()
    common_keys = list(sets.Set(common_map.keys()) - sets.Set(data_keys))
    common_keys.sort()
    env_items = [(k, common_map[k]) for k in common_keys if k.startswith('env_')]
    common_data_items = [(k, common_map[k]) for k in common_keys if k.startswith('data_')]
      
    self.data.update(account = account, product = product, problem = problem,
        occurrences = occurrences, env_items = env_items, common_data_items = common_data_items,
        data_keys = data_keys)
    self.render_and_finish('bug.html')

class PostBugReportHandler(BaseHandler):

  @prolog()
  def post(self, product_name, client_id):
    account = Account.get_or_insert(self.request.host, host = self.request.host)
    product = Product.all().filter('unique_name =', product_name).filter('account =', account).get()
    if product == None:
      self.not_found("Product not found")
      
    client = Client.get_by_id(int(client_id))
    if client_id == None:
      self.not_found("Client not found")
      
    if self.request.get('client_cookie') != client.cookie:
      self.access_denied("Invalid cookie")
    
    problem_hash = self.request.get('problem_hash')
    first_occurrence_at = datetime.fromtimestamp(int(self.request.get('first_occurrence_at')))
    last_occurrence_at = datetime.fromtimestamp(int(self.request.get('last_occurrence_at')))
    count = int(self.request.get('count'))
    
    @transaction
    def create_or_update_problem():
      key_name = 'prob.%s' % problem_hash
      problem = Problem.get_by_key_name(key_name)
      if problem == None:
        problem = Problem(key_name = key_name)
        problem.product = product
        problem.severity = (self.request.get('severity') or 'unknown')
        problem.exception_names = (self.request.get('exception_names') or '').split(',')
        problem.stack_trace = (self.request.get('stack_trace') or None)
        problem.user_message = (self.request.get('user_message') or None)
        problem.developer_message = (self.request.get('developer_message') or None)
        problem.first_occurrence_at = first_occurrence_at
        problem.last_occurrence_at = last_occurrence_at
        problem.occurrence_count = count
      else:
        problem.occurrence_count += count
        if first_occurrence_at < problem.first_occurrence_at:
          problem.first_occurrence_at = first_occurrence_at
        if last_occurrence_at > problem.last_occurrence_at:
          problem.last_occurrence_at = last_occurrence_at
      problem.put()
      return problem
    problem = create_or_update_problem()
    
    hash = self.request.get('hash')
    data = [(k, v) for k, v in self.request.params.iteritems() if k.startswith('data_')]
    env = [(k, v) for k, v in self.request.params.iteritems() if k.startswith('env_')]

    @transaction
    def merge_occurrence():
      key_name = 'occur.%s' % hash
      occurrence = Occurrence.get_by_key_name(key_name)
      if occurrence == None:
        occurrence = Occurrence(key_name = key_name)
        occurrence.first_occurrence_at = first_occurrence_at
        occurrence.last_occurrence_at = last_occurrence_at
        occurrence.count = count
        occurrence.problem = problem
        occurrence.client = client
        
        for k, v in data + env:
          setattr(occurrence, k, v)
      else:
        if occurrence.client.key() != client.key() or occurrence.problem.key() != problem.key():
          self.access_denied("Invalid client or problem of existing occurrence")
        if first_occurrence_at < occurrence.first_occurrence_at:
          occurrence.first_occurrence_at = first_occurrence_at
        if last_occurrence_at > occurrence.last_occurrence_at:
          occurrence.last_occurrence_at = last_occurrence_at
        occurrence.count += count
      occurrence.put()
      return occurrence
      
    occurrence = merge_occurrence()
      
    self.send_urlencoded_and_finish(dict(occurrence_id = occurrence.key().id()))

url_mapping = [
  ('/', MainHandler),
  ('/create-product', CreateProductHandler),
  ('/([a-zA-Z0-9._-]+)/', BugListHandler),
  ('/([a-zA-Z0-9._-]+)/problems/([-a-zA-Z0-9._-]+)', BugHandler),
  ('/([a-zA-Z0-9._-]+)/obtain-client-id', ObtainClientIdHandler),
  ('/([a-zA-Z0-9._-]+)/post-report/([0-9]+)', PostBugReportHandler),
]

def main():
  application = webapp.WSGIApplication(url_mapping,
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
