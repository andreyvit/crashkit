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
from google.appengine.api.labs import taskqueue
from django.utils import simplejson as json
from models import *
from processor import process_report

from controllers.base import *
from commons import *

class AdminHandler(BaseHandler):

  @prolog(fetch=[], check=['is_server_management_allowed'])
  def get(self):
    self.accounts = Account.all().order('-created_at').fetch(100)
    keys_to_accounts = index(lambda a: a.key(), self.accounts)
    products = Product.all().filter('account IN', self.accounts).fetch(1000)
    for k, l in group(lambda p: p._account, products).iteritems():
      keys_to_accounts[k].all_products = l
      
    people = Person.all().fetch(1000)

    self.data.update(tabid='profile-tab', accounts=self.accounts, people=people)
    self.render_and_finish('admin_accounts.html')

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
      return 20, Product.all()
    item.client_admin_password = random_string()
    item.put()
    
  def raise_exception(self):
    self.ppppp
    
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

class AdminFuckUpHandler(BaseHandler):

  @prolog(fetch=[], check=['is_server_management_allowed'])
  def get(self):
    db.Key.from_path('Foo', '123')
    1 / 0

class MigrateHandler(BaseHandler):

  @require_admin
  def get(self):
    taskqueue.add(url='/admin/migrate/worker', params={})
    self.response.out.write("Queued.");

class MigrateWorkerHandler(BaseHandler):
  
  @require_admin
  def post(self):
    start = self.request.get('start')
    total_count = int(self.request.get('count') or 0)

    query = Occurrence.all()
    if start:
      query.filter('__key__ >', db.Key(start))
    old = query.fetch(20)
    if not old:
      logging.info('Migration done after processing %d rows.' % total_count)
      return

    last_key = old[-1].key()
    new = []

    # case_keys = list(set([o._case for o in old]))
    # cases = index(lambda c: c.key(), db.get(case_keys))
    per_week_counts = {}
    per_week_first = {}
    per_week_last = {}
    for occurrence in old:
      # occurrence.bug = cases[occurrence._case]._bug
      occurrence.week = date_to_week(occurrence.date)
      
      if occurrence._bug is None:
        continue
      k = (occurrence._bug, occurrence.week)
      per_week_counts[k] = (per_week_counts.get(k) or 0) + 1
      per_week_first.setdefault(k, occurrence.date)
      per_week_last.setdefault(k, occurrence.date)
      per_week_first[k] = min(per_week_first[k], occurrence.date)
      per_week_last[k]  = max(per_week_last[k], occurrence.date)
    
    db.put(old[0:5])
    db.put(old[5:10])
    db.put(old[10:15])
    db.put(old[15:20])
    
    stats = index(lambda s: (s._bug, s.week), [s for s in BugWeekStat.get_by_key_name([BugWeekStat.key_name_for(b, w) for b,w in per_week_counts]) if s])
    for k in per_week_counts:
      stat = stats.get(k)
      if stat is None:
        stat = BugWeekStat(key_name=BugWeekStat.key_name_for(k[0], k[1]), bug=k[0], week=k[1],
          count=per_week_counts[k], first=per_week_first[k], last=per_week_last[k])
        stats[k] = stat
      else:
        stat.count += per_week_counts[k]
        stat.first = per_week_first[k]
        stat.last = per_week_last[k]
    db.put(stats.values())
      
    # db.put(new)
    # db.delete(old)
    total_count += len(old)
    logging.info("Migration running: processed %d rows" % total_count)

    taskqueue.add(url='/admin/migrate/worker', params=dict(start=last_key, count=total_count))
