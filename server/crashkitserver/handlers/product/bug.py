
class BugHandler(BaseHandler):

  @prolog(fetch=['account', 'product', 'bug'])
  def get(self):
    cases = self.bug.cases.order('-occurrence_count').fetch(100)
    occurrences = Occurrence.all().filter('case IN', cases[:15]).order('-count').fetch(100)
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
        
    details = {}
    for occurrence in occurrences:
      for k in occurrence.dynamic_properties():
        detail = details.get(k)
        if detail is None: details[k] = detail = Detail(key_name=Detail.key_name_for(k))
        v = getattr(occurrence, k)
        try:
          detail.frequencies[detail.values.index(v)] += 1
        except ValueError:
          detail.values.append(v)
          detail.frequencies.append(1)
          
    # keep it sorted
    for detail in details.itervalues():
      data = sorted(zip(detail.values, detail.frequencies), lambda a,b: 0 if a[1] == b[1] else (1 if a[1] < b[1] else -1))
      detail.values      = [pair[0] for pair in data]
      detail.frequencies = [pair[1] for pair in data]
      
    # group
    (GET_details, POST_details, COOKIE_details, SESSION_details, custom_details, essential_REQUEST_details, REQUEST_details,
      SERVER_details, env_details) = [], [], [], [], [], [], [], [], []
    for k, detail in details.iteritems():
      if k.startswith('data_G_') or k.startswith('data_GET_'):
        GET_details.append(detail)
      elif k.startswith('data_P_') or k.startswith('data_POST_'):
        POST_details.append(detail)
      elif k.startswith('data_C_'):
        COOKIE_details.append(detail)
      elif k.startswith('data_S_'):
        SESSION_details.append(detail)
      elif k.startswith('env_'):
        name = k[4:]
        if name in IGNORED_VARS:
          pass
        elif name in SERVER_DETAIL_VARS:
          SERVER_details.append(detail)
        elif name in REQUEST_DETAIL_VARS:
          REQUEST_details.append(detail)
        elif name in ESSENTIAL_REQUEST_DETAILS:
          essential_REQUEST_details.append(detail)
        else:
          env_details.append(detail)
      else:
        custom_details.append(detail)
        
    cover_case = cases[0]
    for case in cases:
      if len(case.exceptions) < len(cover_case.exceptions):
        cover_case = case
        
    # data_keys contains all columns that differ across occurrences
    data_keys = [] #list(sets.Set(flatten([ [k for k in o.dynamic_properties() if k in common_map and len(common_map[k])>1] for o in occurrences ])))
    data_keys.sort()
    common_keys = [] #list(sets.Set(common_map.keys()) - sets.Set(data_keys))
    # common_keys.sort()
    # env_items = [(k, common_map[k]) for k in common_keys if k.startswith('env_')]
    # common_data_items = [(k, common_map[k]) for k in common_keys if k.startswith('data_')]
      
    self.data.update(tabid = 'bug-tab', bug_id=True,
        cases=cases, cover_case=cover_case,
        occurrences = occurrences, data_keys = data_keys, cover_message=cover_message,
        GET_details=GET_details, POST_details=POST_details,
        COOKIE_details=COOKIE_details, SESSION_details=SESSION_details,
        custom_details=custom_details,
        essential_REQUEST_details=essential_REQUEST_details, REQUEST_details=REQUEST_details,
        SERVER_details=SERVER_details, env_details=env_details)
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

class ChangeBugStateHandler(BaseHandler):
  
  @prolog(fetch=['account', 'product', 'bug'], check=['is_product_write_allowed'])
  def post(self):
    if self.request.get('open'):
      new_state = 'reopen'
    elif self.request.get('close'):
      new_state = 'close'
    elif self.request.get('ignore'):
      new_state = 'ignore'
      
    def txn(bug_key=self.bug.key()):
      b = Bug.get(bug_key)
      if getattr(b, new_state)():
        b.put()
    db.run_in_transaction(txn, self.bug.key())
    
    self.redirect_and_finish(".")


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

url_mapping = (
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/', BugHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/assign-ticket', AssignTicketToBugHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/bugs/([a-zA-Z0-9._-]+)/change-state', ChangeBugStateHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/blob/([a-zA-Z0-9]+)/', ViewBlobHandler),
)
