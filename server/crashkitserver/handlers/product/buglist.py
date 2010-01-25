
class BugListHandler(BaseHandler):

  def show_bug_list(self):
    week_count = 4
    
    bugs = self.bugs_query_filter(self.product.bugs).order('-last_occurrence_on').fetch(1000)
    bugs_by_key = index_by_key(bugs)
    
    interesting_stat_keys = []
    for bug in bugs:
      interesting_stat_keys += [BugWeekStat.key_name_for(bug.key(), date_to_week(bug.last_occurrence_on - timedelta(days=7*i))) for i in range(week_count)]
    stats = BugWeekStat.get_by_key_name(interesting_stat_keys)
    stats = group(lambda s: s._bug, filter(lambda s: s is not None, stats))
    stats = dict([ (b, BugWeekStat.sum(ss, previous_week(date_to_week(bugs_by_key[b].last_occurrence_on), offset=week_count), date_to_week(bugs_by_key[b].last_occurrence_on))) for b,ss in stats.items() ])
    
    for bug in bugs:
      bug.stats = stats.get(bug.key())
    bugs = filter(lambda b: b.stats is not None, bugs)
    
    def sort_bugs_of_a_week(week_start, week_end, bugs):
      for bug in bugs:
        bug.is_new_on_last_week = between(bug.created_at.date(), week_start, week_end)
      return sorted(bugs, lambda a,b: -10*signum(a.is_new_on_last_week-b.is_new_on_last_week) -signum(a.stats.count-b.stats.count))
    
    grouped_bugs = group(lambda bug: date_to_week(bug.last_occurrence_on), bugs).items()
    grouped_bugs = sorted(grouped_bugs, lambda a,b: -signum(a[0]-b[0]))
    grouped_bugs = [ (week, week_to_start_date(week), week_to_end_date(week), bugs ) for week, bugs in grouped_bugs ]
    grouped_bugs = [ (week, week_start, week_end, sort_bugs_of_a_week(week_start, week_end, bugs)) for week, week_start, week_end, bugs in grouped_bugs ]
    
    self.data.update(grouped_bugs=grouped_bugs)
    self.render_and_finish('buglist.html')

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.data.update(tabid = 'bugs-tab')
    self.data.update(mass_actions=dict(reopen=False, close=True, ignore=True))
    self.show_bug_list()

  def bugs_filter(self, bugs):
    return filter(lambda b: b.state == BUG_OPEN, bugs)

  def bugs_query_filter(self, bugs):
    return bugs.filter('state', BUG_OPEN)

class ClosedBugListHandler(BugListHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.data.update(tabid = 'closed-bugs-tab')
    self.data.update(mass_actions=dict(reopen=True, close=False, ignore=False))
    self.show_bug_list()

  def bugs_filter(self, bugs):
    return filter(lambda b: b.state == BUG_CLOSED, bugs)

  def bugs_query_filter(self, bugs):
    return bugs.filter('state', BUG_CLOSED)

class IgnoredBugListHandler(BugListHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    self.data.update(tabid = 'ignored-bugs-tab')
    self.data.update(mass_actions=dict(reopen=True, close=False, ignore=False))
    self.show_bug_list()

  def bugs_filter(self, bugs):
    return filter(lambda b: b.state == BUG_IGNORED, bugs)

  def bugs_query_filter(self, bugs):
    return bugs.filter('state', BUG_IGNORED)

class RecentCaseListHandler(BaseHandler):

  @prolog(fetch=['account', 'product'])
  def get(self):
    bugs = self.product.bugs.order('-occurrence_count').fetch(100)
    self.data.update(bugs = bugs)
    self.render_and_finish('buglist.html')
    
SERVER_DETAIL_VARS = ['GATEWAY_INTERFACE', 'SERVER_NAME', 'SERVER_PORT', 'SERVER_SOFTWARE']
ESSENTIAL_REQUEST_DETAILS = ['REQUEST_METHOD', 'CONTENT_TYPE']
REQUEST_DETAIL_VARS = ['HTTP_ACCEPT', 'HTTP_ACCEPT_ENCODING', 'HTTP_ACCEPT_LANGUAGE',
    'HTTP_HOST', 'HTTP_REFERER', 'HTTP_USER_AGENT', 'PATH_INFO', 'REMOTE_ADDR', 'REMOTE_HOST']
IGNORED_VARS = ['hash', 'Apple_PubSub_Socket_Render', 'COMMAND_MODE', 'CONTENT_LENGTH', 'DISPLAY',
    'DJANGO_SETTINGS_MODULE', 'HOME', 'HTTP_CONNECTION', 'HTTP_COOKIE', 'HTTP_ORIGIN', 'LC_CTYPE',
    'LOGNAME', 'MANPATH', 'OLDPWD', 'PATH', 'PWD', 'QUERY_STRING', 'RUN_MAIN', 'SERVER_PROTOCOL',
    'HTTP_CACHE_CONTROL']


class MassBugStateEditHandler(BaseHandler):
  
  @prolog(fetch=['account', 'product'], check=['is_product_write_allowed'])
  def post(self):
    action = self.request.get('action')
    key_names = map(lambda s: s.strip(), self.request.get('bugs').strip().split("\n"))
    
    logging.info(repr(key_names))
    
    if action in ['reopen', 'close', 'ignore']:
      new_state = action
    else:
      self.error(400)
      self.response.out.write("Invalid action: '%s'" % action)
      return

    bugs = Bug.get_by_key_name(key_names)
    bugs = filter(lambda b: b is not None, bugs)
    dirty_bugs = []
    for bug in bugs:
      if bug._product != self.product.key():
        self.error(400)
        self.response.out.write("Invalid reference to a bug from another product: '%s'" % bug.key().name())
        return
      if getattr(bug, new_state)():
        dirty_bugs.append(bug)
    db.put(dirty_bugs)
    
    self.redirect_and_finish(".")

url_mapping = (
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/', BugListHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/closed', ClosedBugListHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/ignored', IgnoredBugListHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/mass-state-edit', MassBugStateEditHandler),
)
