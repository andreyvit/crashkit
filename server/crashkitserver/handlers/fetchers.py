
from yoursway.web.handling import fetcher, before_request, NotFound
from models import Account

@fetcher
def with_account(self, account_permalink):
  # host = self.request.host
  # if host = 'feedback.yoursway.com' or host = 'localhost':
  #   self.account = Account.all().filter('host =', self.request.host)
  self.account = Account.all().filter('permalink =', account_permalink).get()
  if self.account is None:
    raise NotFound, "Account %s does not exist." % account_permalink
    
  self.account_access = self.person.account_access_for(self.account)
  self.account_path = '/%s' % self.account.permalink
    
@before_request
def with_new_account(self):
  self.account = Account(permalink='')
  
def fetch_product_nocheck(self, product_name):
  self.product = self.account.products.filter('unique_name =', product_name).get()
  if self.product == None:
    self.not_found("Product not found")
  self.product_path = '%s/products/%s' % (self.account_path, self.product.unique_name)
  self.data.update(product=self.product, product_path=self.product_path)
  
def fetch_product(self, product_name):
  self.fetch_product_nocheck(product_name)
  
  self.product_access = self.account_access.product_access_for(self.product)
  if not self.product_access.is_viewing_allowed():
    self.access_denied("Sorry, you do not have access to this product.")
  self.data.update(product_access=self.product_access)
  
def fetch_or_create_product(self, product_name):
  if product_name == 'new':
    self.product = Product(account=self.account,name='',permalink='')
    self.product_access = None
    self.data.update(product=self.product)
  else:
    self.fetch_product(product_name)

def fetch_bug(self, bug_name):
  self.bug = Bug.get_by_key_name(bug_name)
  if self.bug == None or self.bug.product.key() != self.product.key():
    self.not_found("Bug not found")
  self.data.update(bug=self.bug)
  
def fetch_client(self, client_id):
  if client_id == '0':
    k = 'P%s-anonymous' % self.product.key().id_or_name()
    self.client = Client.get_by_key_name(k)
    if not self.client:
      self.client = Client.get_or_insert(k, product=self.product, cookie='0')
    return

  self.client = Client.get_by_id(int(client_id))
  if self.client == None:
    logging.warn('Client ID requested but not found: "%s"' % client_id)
    self.blow(403, 'invalid-client-id')
  self.data.update(client=self.client)

def fetch_client_cookie(self, client_cookie):
  if client_cookie != self.client.cookie:
    logging.warn('Client ID cookie invalid: "%s" / "%s"' % (client_id, client_cookie))
    self.blow(403, 'invalid-client-id')
    
def fetch_account_authorizations(self):
  self.account_authorizations = self.person.account_authorizations.fetch(100)
  for account in self.account_authorizations:
    account.product_authorizations = []
  keys_to_account_authorizations = index(lambda m: m._account, self.account_authorizations)
  product_auth = self.person.product_authorizations.fetch(100)
  keys_to_products = index(lambda m: m.key(), Product.get([a._product for a in product_auth]))
  for product_key, authorizations in group(lambda p: p._product, product_auth).iteritems():
    product = keys_to_products[product_key]
    if product:
      account = keys_to_account_authorizations[product._account]
      if account:
        account.product_authorizations += authorizations
    