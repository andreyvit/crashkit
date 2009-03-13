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
from controllers.product import *
from controllers.account import *
from controllers.invites import *
from commons import *

class HomeHandler(BaseHandler):
  
  @prolog()
  def get(self):
    self.render_and_finish('site_home.html')

class AccountDashboardHandler(BaseHandler):

  @prolog(fetch = ['account'])
  def get(self):
    products = self.account.products.order('unique_name').fetch(100)
    for product in products:
      access = self.account_access.product_access_for(product)
      product.access = access
    products = filter(lambda p: p.access.is_listing_allowed(), products)
    for product in products:
      new_bugs = product.bugs.filter('ticket =', None).order('-occurrence_count').fetch(7)
      product.more_new_bugs = (len(new_bugs) == 7)
      product.new_bugs = new_bugs[0:6]
      product.new_bug_count = len(product.new_bugs)
    
    self.data.update(tabid='dashboard-tab', account=self.account, products=products)
    self.render_and_finish('account_dashboard.html')

class ObtainClientIdHandler(BaseHandler):

  @prolog(fetch=['account', 'product_nocheck'])
  def get(self):
    client = Client()
    client.product = self.product
    client.cookie = random_string()
    client.put()
    self.send_urlencoded_and_finish(response = 'ok', client_id = client.key().id(), client_cookie = client.cookie)

class CompatObtainClientIdHandler(BaseHandler):

  @prolog(fetch=['compat_account', 'product_nocheck'])
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
    
    self.data.update(compartments=compartments)
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
    
    messages = []
    for o in occurrences:
      mm = o.exception_messages
      if not isinstance(mm, list):
        mm = [mm]
      for m in mm:
        messages.append(m)
    messages = list(sets.Set(messages))
    cover_message = None
    for message in messages:
      if cover_message is None or len(message) < len(cover_message):
        cover_message = message

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
      
    self.data.update(tabid = 'bug-tab', bug_id=True,
        cases=cases, cover_case=cover_case,
        occurrences = occurrences, env_items = env_items, common_data_items = common_data_items,
        data_keys = data_keys, cover_message=cover_message)
    self.render_and_finish('bug.html')

class AssignTicketToBugHandler(BaseHandler):
  
  @prolog(fetch=['account', 'product', 'bug'], check=['is_product_write_allowed'])
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

class CompatPostBugReportHandler(BaseHandler):

  @prolog(fetch=['compat_account', 'product_nocheck', 'client', 'client_cookie'])
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

class PostBugReportHandler(BaseHandler):

  @prolog(fetch=['account_nocheck', 'product_nocheck', 'client', 'client_cookie'])
  def post(self):
    body = unicode((self.request.body or ''), 'utf-8').strip()
    if len(body) == 0:
      self.blow(400, 'json-payload-required')
    
    report = Report(product=self.product, client=self.client, remote_ip=self.request.remote_addr,
        data=body)
    report.put()
    
    all_blobs = re.findall('"blob:([a-zA-Z0-9]+)"', body)
    existing_blobs = Attachment.get_by_key_name([Attachment.key_name_for(self.product.key(), b) for b in all_blobs])
    blobs = sets.Set(all_blobs) - sets.Set([b.body_hash for b in existing_blobs if b])
    logging.warn("BLOBS TO GET: %s,  all blobs: %s", ','.join(blobs), ','.join(all_blobs))
    
    process_report(report)
      
    self.send_urlencoded_and_finish(response = 'ok', status = report.status,
        error = (report.error or 'none'), blobs=','.join(blobs))
  get=post

class PostBlobHandler(BaseHandler):

  @prolog(fetch=['account_nocheck', 'product_nocheck', 'client', 'client_cookie'])
  def post(self, body_hash):
    body = (unicode(self.request.body, 'utf-8') or u'')
    def txn():
      k = Attachment.key_name_for(self.product.key(), body_hash)
      a = Attachment.get_by_key_name(k)
      if not a:
        a = Attachment(key_name=k, product=self.product, client=self.client, body=body,
            body_hash=body_hash)
        a.put()
    db.run_in_transaction(txn)
  
    self.send_urlencoded_and_finish(response='ok')
  get=post

class ViewBlobHandler(BaseHandler):

  @prolog(fetch=['account', 'product'])
  def get(self, body_hash):
    k = Attachment.key_name_for(self.product.key(), body_hash)
    self.attachment = Attachment.get_by_key_name(k)
    if self.attachment is None:
      self.response.out.write("not found")
    else:
      self.response.headers['Content-Type'] = "text/plain"
      self.response.out.write(self.attachment.body)
  
class Temp(BaseHandler):
  @prolog(check=['is_server_management_allowed'])
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
    
  def convert_exception_messages(self, item):
    if item == None:
      return 40, Occurrence.all()
    mm = item.exception_messages
    if isinstance(mm, unicode):
      item.exception_messages = [db.Text(x) for x in eval(mm)]
      item.put()
      
  def delete_all_cases(self, item):
    if item == None:
      return 40, Case.all()
    item.delete()
      
  def delete_all_bugs(self, item):
    if item == None:
      return 40, Bug.all()
    item.delete()
      
  def zero_all_bugs_stats(self, item):
    if item == None:
      return 40, Bug.all()
    item.occurrence_count = 0
    item.roles = []
    item.put()
      
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
    process_case(item.product, item, item.occurrence_count)
      
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

url_mapping = [
  ('/', HomeHandler),
  ('/signup/([a-zA-Z0-9]*)', SignupHandler),
  ('/betasignup/', SignUpForLimitedBetaHandler),
  ('/beta/', LimitedBetaCandidateListHandler),
  ('/beta/accept', LimitedBetaAcceptCandidateHandler),
  ('/beta/reject', LimitedBetaRejectCandidateHandler),
  ('/iterate', Temp),
  # per-account
  ('/([a-zA-Z0-9._-]+)/', AccountDashboardHandler),
  ('/([a-zA-Z0-9._-]+)/people/', AccountPeopleHandler),
  ('/([a-zA-Z0-9._-]+)/settings/', AccountSettingsHandler),
  # per-project API (compatibility)
  ('/([a-zA-Z0-9._-]+)/obtain-client-id', CompatObtainClientIdHandler),
  ('/([a-zA-Z0-9._-]+)/post-report/([0-9]+)/([a-zA-Z0-9]+)', CompatPostBugReportHandler),
  # per-project API
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/obtain-client-id', ObtainClientIdHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/post-report/([0-9]+)/([a-zA-Z0-9]+)', PostBugReportHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/post-blob/([0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', PostBlobHandler),
  # per-project (users)
  ('/([a-zA-Z0-9._-]+)/products/(new)/', ProductSettingsHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/', NewBugListHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/settings', ProductSettingsHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/all', AllBugListHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/', BugHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/assign-ticket', AssignTicketToBugHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/blob/([a-zA-Z0-9]+)/', ViewBlobHandler),
]

def main():
  application = webapp.WSGIApplication(url_mapping,
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
