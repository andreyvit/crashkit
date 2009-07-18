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


class MigrateHandler(BaseHandler):

  @require_admin
  def get(self):
    taskqueue.add(url='/admin/migrate/worker', params={})
    self.response.out.write("Queued.");

class MigrateWorkerHandler(BaseHandler):

  @require_admin
  def post(self):
    pass
  
  def do_bug_state_migration(self):
    start = self.request.get('start')
    total_count = int(self.request.get('count') or 0)

    query = Bug.all()
    if start:
      query.filter('__key__ >', db.Key(start))
    old = query.fetch(20)
    if not old:
      logging.info('Migration done after processing %d rows.' % total_count)
      return

    last_key = old[-1].key()
    new = []

    for bug in old:
      bug.state = BUG_OPEN
    
    db.put(old)
    
    total_count += len(old)
    logging.info("Migration running: processed %d rows" % total_count)

    taskqueue.add(url='/admin/migrate/worker', params=dict(start=last_key, count=total_count))
  

  def add_weekly_stats_migration(self):
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
      
    total_count += len(old)
    logging.info("Migration running: processed %d rows" % total_count)

    taskqueue.add(url='/admin/migrate/worker', params=dict(start=last_key, count=total_count))
