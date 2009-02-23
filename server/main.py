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

template_path = os.path.join(os.path.dirname(__file__), 'templates')
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

class MainHandler(BaseHandler):

  @prolog(fetch = ['account'])
  def get(self):
    products = self.account.products.order('unique_name').fetch(100)
    for product in products:
      new_bugs = product.bugs.filter('ticket =', None).order('-occurrence_count').fetch(7)
      product.more_new_bugs = (len(new_bugs) == 7)
      product.new_bugs = new_bugs[0:6]
      product.new_bug_count = len(product.new_bugs)
    
    self.data.update(tabid='home-tab', account=self.account, products=products)
    self.render_and_finish('home.html')

class CreateProductHandler(BaseHandler):

  @prolog(fetch = ['account'])
  def get(self):
    product = Product.all().filter('unique_name =', self.request.get('unique_name')).get()
    if product == None:
      product = Product()
    product.account = self.account
    product.unique_name = self.request.get('unique_name')
    product.friendly_name = self.request.get('friendly_name')
    product.put()
      
    self.send_urlencoded_and_finish(response = 'ok', host = self.request.host)

class ObtainClientIdHandler(BaseHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    client = Client()
    client.product = self.product
    client.cookie = random_string()
    client.put()
    self.send_urlencoded_and_finish(response = 'ok', client_id = client.key().id(), client_cookie = client.cookie)

class BugListHandler(BaseHandler):

  def show_bug_list(self, all_bugs):
    compartments = [
      dict(
        title = "Bugs experienced only by developers",
        bugs  = filter(lambda b: not(u'customer' in b.roles or u'tester' in b.roles), all_bugs().filter('roles =', 'developer').fetch(100))),
      dict(
        title = "Bugs experienced only by developers and testers",
        bugs  = filter(lambda b: not(u'customer' in b.roles), all_bugs().filter('roles =', 'tester').fetch(100))),
      dict(
        title = "Bugs experienced by customers",
        bugs  = all_bugs().filter('roles =', 'customer').fetch(100))]
    
    self.data.update(product_path=".", compartments=compartments)
    self.render_and_finish('buglist.html')

class NewBugListHandler(BugListHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.data.update(tabid = 'new-tab')
    self.show_bug_list(self.all_bugs)

  def all_bugs(self):
    return self.product.bugs.order('-occurrence_count').filter('ticket =', None)

class AllBugListHandler(BugListHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.data.update(tabid = 'all-tab')
    self.show_bug_list(self.all_bugs)

  def all_bugs(self):
    return self.product.bugs.order('-occurrence_count')

class RecentCaseListHandler(BaseHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    bugs = self.product.bugs.order('-occurrence_count').fetch(100)
    self.data.update(bugs = bugs)
    self.render_and_finish('buglist.html')

class BugHandler(BaseHandler):

  @prolog(fetch=['account', 'product', 'bug'])
  def get(self):
    cases = self.bug.cases.order('-occurrence_count').fetch(100)
    occurrences = Occurrence.all().filter('case IN', cases).order('-count').fetch(100)
    clients = Client.get([o.client.key() for o in occurrences])

    common_map = dict()
    for key in sets.Set(flatten([ [k for k in o.dynamic_properties() if k.startswith('env_') or k.startswith('data_')] for o in occurrences ])):
      set = sets.Set([s for s in [getattr(o, key) for o in occurrences if hasattr(o, key)] if s != None and len(s) > 0])
      if len(set) > 0:
        common_map[key] = set
    if 'env_hash' in common_map:
      del common_map['env_hash']
      
    cover_case = cases[0]
    for case in cases:
      if len(case.exceptions) < len(cover_case.exceptions):
        cover_case = case
    
    # data_keys contains all columns that differ across occurrences
    data_keys = list(sets.Set(flatten([ [k for k in o.dynamic_properties() if k in common_map and len(common_map[k])>1] for o in occurrences ])))
    data_keys.sort()
    common_keys = list(sets.Set(common_map.keys()) - sets.Set(data_keys))
    common_keys.sort()
    env_items = [(k, common_map[k]) for k in common_keys if k.startswith('env_')]
    common_data_items = [(k, common_map[k]) for k in common_keys if k.startswith('data_')]
      
    self.data.update(tabid = 'bug-tab', product_path="../..", bug_id=True,
        cases=cases, cover_case=cover_case,
        occurrences = occurrences, env_items = env_items, common_data_items = common_data_items,
        data_keys = data_keys)
    self.render_and_finish('bug.html')

class AssignTicketToBugHandler(BaseHandler):
  
  @prolog(fetch=['account', 'product', 'bug'])
  def post(self):
    ticket_name = self.request.get('ticket')
    if ticket_name == None or len(ticket_name.strip()) == 0:
      ticket = None
    else:
      ticket = Ticket.get_or_insert(key_name=Ticket.key_name_for(self.product.key().id_or_name(), ticket_name),
          product=self.product, name=ticket_name)
      
    def txn(bug_key):
      b = Bug.get(bug_key)
      b.ticket = ticket
      b.put()
    db.run_in_transaction(txn, self.bug.key())
    
    self.redirect_and_finish(".")

class PostBugReportHandler(BaseHandler):

  @prolog(fetch=['account', 'product', 'client', 'client_cookie'])
  def post(self):
    body = (self.request.body or '').strip()
    if len(body) == 0:
      self.blow(400, 'json-payload-required')
    
    report = Report(product=self.product, client=self.client, remote_ip=self.request.remote_addr,
        data=unicode(self.request.body, 'utf-8'))
    report.put()
    
    process_report(report)
      
    self.send_urlencoded_and_finish(response = 'ok', status = report.status, error = (report.error or 'none'))
  get=post
  
class Temp(BaseHandler):
  # @prolog()
  def get(self):
    func_name = self.request.get('func')
    func = None
    if func_name:
      try:
        func = getattr(self, func_name.replace('-', '_'))
      except AttributeError:
        pass
        
    if func:
      batch_size, items = func(None)
      if self.request.get('batchsize'):
        batch_size = int(self.request.get('batchsize'))
        
      start_key = self.request.get('key')
      if start_key:
        items = items.filter('__key__ >', db.Key(start_key))
        
      items = items.order('__key__').fetch(batch_size)
      for item in items:
        func(item)
        
      total_processed = len(items)
      if self.request.get('total'):
        total_processed += int(self.request.get('total'))
      self.response.out.write("<p>%d items this time, %d items total.<br>" % (len(items), total_processed))
      
      last_key = None if len(items) < batch_size else str(items[-1].key())
      if last_key:
        self.response.out.write("""<h2>Continue %s</h2>\n""" % func_name);
        self.response.out.write("""<form action="/iterate" method="GET">\n""");
        self.response.out.write("""<input type="hidden" name="func" value="%s">\n""" % func_name);
        self.response.out.write("""<input type="hidden" name="total" value="%d">\n""" % total_processed);
        self.response.out.write("""<input type="hidden" name="key" value="%s">\n""" % last_key);
        self.response.out.write("""<p>Batch size: <input type="text" name="batchsize" size="5" value="%d">\n""" % batch_size);
        self.response.out.write("""<input type="submit" value="Continue %s">\n""" % func_name);
        self.response.out.write("""</form>\n""");
      else:
        self.response.out.write("""<h2>%s done</h2>\n""" % func_name);
      
    self.response.out.write("""<h2>Start iteration</h2>\n""");
    self.response.out.write("""<p><a href="/iterate">Refresh list of methods</a></p>\n""");
    self.response.out.write("""<form action="/iterate" method="GET">\n""");
    for func in filter(lambda f: not(f.startswith('__') or f == 'get'), self.__class__.__dict__.keys()):
      self.response.out.write("""<input type="submit" name="func" value="%s">\n""" % func.replace('_', '-'));
    self.response.out.write("""</form>\n""");
      
    
  def temp(self, item):
    if item == None:
      return 20, Bug.all()
    item.ticket = None
    item.put()
      
  def delete_all_cases(self, item):
    if item == None:
      return 40, Case.all()
    item.delete()
      
  def delete_all_bugs(self, item):
    if item == None:
      return 40, Bug.all()
    item.delete()
      
  def delete_all_occurrences(self, item):
    if item == None:
      return 100, Occurrence.all()
    item.delete()
    
  def clear_bugs_from_cases(self, item):
    if item == None:
      return 20, Case.all().filter('bug !=', None)
    item.bug = None
    item.put()
    
  def assign_bugs_to_cases_without_bugs(self, item):
    if item == None:
      return 20, Case.all().filter('bug =', None)
    process_case(item)
      
  def requeue_all_reports(self, item):
    if item == None:
      return 40, Report.all().filter('status =', 1)
    item.status = 0
    item.put()

  def process_pending_reports(self, item):
    if item == None:
      return 40, Report.all().filter('status =', 0)
    try:
      process_report(item)
    except Exception, e:
      item.status = 2
      item.put()
      self.response.out.write("""<div>Error: %s %s</div>""" % (e.__class__.__name__, e.message));
      
    
class ProcessPendingReportsHandler(BaseHandler):
  
  @prolog()
  def get(self):
    self.account = Account.get_or_insert(self.request.host, host = self.request.host)
    report = self.account.reports.filter('status =', 0).get()
    if report == None:
      self.send_urlencoded_and_finish(response = 'no-more')
    process_report(report)
    self.send_urlencoded_and_finish(response = 'done', report_key = report.key())

url_mapping = [
  ('/', MainHandler),
  ('/create-product', CreateProductHandler),
  ('/process', ProcessPendingReportsHandler),
  ('/iterate', Temp),
  ('/([a-zA-Z0-9._-]+)/', NewBugListHandler),
  ('/([a-zA-Z0-9._-]+)/all', AllBugListHandler),
  ('/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/', BugHandler),
  ('/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/assign-ticket', AssignTicketToBugHandler),
  ('/([a-zA-Z0-9._-]+)/obtain-client-id', ObtainClientIdHandler),
  ('/([a-zA-Z0-9._-]+)/post-report/([0-9]+)/([a-zA-Z0-9]+)', PostBugReportHandler),
]

def main():
  application = webapp.WSGIApplication(url_mapping,
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
