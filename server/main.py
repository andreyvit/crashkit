# -*- coding: utf-8

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from yoursway.web.app import load_url_mapping

url_mapping = load_url_mapping(
  # 'crashkitserver.handlers.general.admin',
  'crashkitserver.handlers.general.marketingsite',
  # 'crashkitserver.handlers.general.migration',
  # 'crashkitserver.handlers.general.reportqueue',
  'crashkitserver.handlers.general.status',
  # 'crashkitserver.handlers.api.api00',
  # 'crashkitserver.handlers.api.api0',
  # 'crashkitserver.handlers.api.api1',
  # 'crashkitserver.handlers.account.account',
  'crashkitserver.handlers.account.accountedit',
  'crashkitserver.handlers.account.invites',
  # 'crashkitserver.handlers.account.user',
  # 'crashkitserver.handlers.product.bug',
  # 'crashkitserver.handlers.product.buglist',
  # 'crashkitserver.handlers.product.product',
  'crashkitserver.handlers.general.fourohfour',
)

application = webapp.WSGIApplication(url_mapping, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
