
from crashkitserver.commons import fetch_compat_account

@before_request
def fetch_compat_account(self):
  self.account = Account.all().filter('permalink', 'ys').get()
  self.account_access = self.person.account_access_for(self.account)
  self.account_path = '/%s' % self.account.permalink

class CompatObtainClientIdHandler(BaseHandler):

  @fetch_compat_account
  @fetch_product_nocheck
  def get(self):
    client = Client()
    client.product = self.product
    client.cookie = random_string()
    client.put()
    self.send_urlencoded_and_finish(response = 'ok', client_id = client.key().id(), client_cookie = client.cookie)

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


url_mapping = (
  ('/([a-zA-Z0-9._-]+)/obtain-client-id', CompatObtainClientIdHandler),
  ('/([a-zA-Z0-9._-]+)/post-report/([0-9]+)/([a-zA-Z0-9]+)', CompatPostBugReportHandler),
)
