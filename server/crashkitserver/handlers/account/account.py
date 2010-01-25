
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

url_mapping = (
  ('/([a-zA-Z0-9._-]+)/', AccountDashboardHandler),
)
