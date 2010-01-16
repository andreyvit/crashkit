import atexit
import code
import getpass
import optparse
import os
import readline
import sys

from google.appengine.ext.remote_api import remote_api_stub

from google.appengine.api import datastore
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import search

from models import *


HISTORY_PATH = os.path.expanduser('~/.remote_api_shell_history')
DEFAULT_PATH = '/remote_api'
BANNER = """App Engine remote_api shell
Python %s
The db, users, urlfetch, and memcache modules are imported.""" % sys.version


def auth_func():
  return (raw_input('Email: '), getpass.getpass('Password: '))
  sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))



def active_users():
  global pp
  def print_product(p):
    print '%s %s %s %s' % (p.unique_name, p.account.name, p.max_week, " ".join([a.person.user.email() for a in ProductAccess.all().filter('product', p).fetch(100) if a.level == ACCESS_ADMIN]))
  pp = Product.all().fetch(100)
  for p in pp:
    b = BugWeekStat.all().filter('product', p).order('-week').get()
    if b is None:
      p.max_week = 0
    else:
      p.max_week = b.week
      print_product(p)
  pp = sorted(pp, (lambda x, y: -int(x.max_week - y.max_week)))
  print "==============================="
  for p in pp:
    print_product(p)

def print_active_users():
  global pp
  def print_product(p):
    print '%s/%s %s -- %s' % (p.account.permalink, p.unique_name, p.max_week, " ".join([a.person.user.email() for a in ProductAccess.all().filter('product', p).fetch(100) if a.level == ACCESS_ADMIN]))
  pp = sorted(pp, (lambda x, y: -int(x.max_week - y.max_week)))
  print "==============================="
  for p in pp:
    if p.max_week == 0: continue
    print_product(p)


def main(argv):
  parser = optparse.OptionParser()
  parser.add_option('-s', '--server', dest='server',
                    help='The hostname your app is deployed on. '
                         'Defaults to <app_id>.appspot.com.')
  (options, args) = parser.parse_args()

  if not args or len(args) > 2:
    print >> sys.stderr, __doc__
    if len(args) > 2:
      print >> sys.stderr, 'Unexpected arguments: %s' % args[2:]
    sys.exit(1)

  appid = args[0]
  if len(args) == 2:
    path = args[1]
  else:
    path = DEFAULT_PATH

  remote_api_stub.ConfigureRemoteApi(appid, path, auth_func,
                                     servername=options.server)
  remote_api_stub.MaybeInvokeAuthentication()

  readline.parse_and_bind('tab: complete')
  atexit.register(lambda: readline.write_history_file(HISTORY_PATH))
  sys.ps1 = '%s> ' % appid
  if os.path.exists(HISTORY_PATH):
    readline.read_history_file(HISTORY_PATH)

  code.interact(banner=BANNER, local=globals())


if __name__ == '__main__':
  main()
  
  
