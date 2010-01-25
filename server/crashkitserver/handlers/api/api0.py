
class ObtainClientIdHandler(BaseHandler):

  @prolog(fetch=['account', 'product_nocheck'])
  def get(self):
    client = Client()
    client.product = self.product
    client.cookie = random_string()
    client.put()
    self.send_urlencoded_and_finish(response = 'ok', client_id = client.key().id(), client_cookie = client.cookie)

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
    
    taskqueue.add(url = '/qworkers/process-report', params = {'key': report.key().id()})
      
    self.send_urlencoded_and_finish(response = 'ok', status = report.status,
        error = (report.error or 'none'), blobs=','.join(blobs))
  get=post

  def handle_exception(self, exception, debug_mode):
    return webapp.RequestHandler.handle_exception(self, exception, debug_mode)


class ObtainLastReportHandler(BaseHandler):

  @prolog(fetch=['account_nocheck', 'product_nocheck'])
  def get(self):
    report = Report.all().filter('product', self.product).order('-created_at').get()
    if report is None:
      self.response.out.write('[]')
    else:
      self.response.out.write(report.data)

  def handle_exception(self, exception, debug_mode):
    return webapp.RequestHandler.handle_exception(self, exception, debug_mode)


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

url_mapping = (
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/obtain-client-id', ObtainClientIdHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/post-report/([0-9]+)/([a-zA-Z0-9]+)', PostBugReportHandler),
  ('/([a-zA-Z0-9._-]+)/products/([a-zA-Z0-9._-]+)/post-blob/([0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', PostBlobHandler),
  ('/(test)/products/([a-zA-Z0-9._-]+)/last-posted-report', ObtainLastReportHandler),
)
