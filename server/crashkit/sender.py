
__all__ = ['initialize_crashkit', 'send_exception']

from jsonencoder import JSONEncoder
from traceback import extract_tb
from types import ClassType
from datetime import date
import sys

enc = JSONEncoder()

class CrashKit:
  
  def __init__(self, account_name, product_name):
    self.account_name = account_name
    self.product_name = product_name
    self.post_url = "http://crashkitapp.appspot.com/%s/products/%s/post-report/0/0" % (
        self.account_name, self.product_name)

  def send_exception(self, data = {}, env = {}):
    if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
      return # Google App Engine development server, do not report errors
      
    info = sys.exc_info()
    traceback = get_traceback(info[2])
    env = dict(**env)
    env.update(**collect_platform_info())
    message = {
        "date": date.today().strftime("%Y-%m-%d"),
        "exceptions": [
            {
                "name": encode_exception_name(info[0]),
                "message": info[1].message,
                "locations": [encode_location(el) for el in traceback]
            }
        ],
        "data": data,
        "env": env,
        "language": "python",
    }
    payload = enc.encode([message]).replace('{', "\n{")
    from urllib2 import Request, urlopen, HTTPError, URLError
    try:
      response = urlopen(Request(self.post_url, payload))
      the_page = response.read()
      print unicode(the_page, 'utf-8')
    except UnicodeDecodeError:
      pass
    except HTTPError, e:
      print "Cannot send exception - HTTP error %s" % e.code
      try:
        print unicode(e.read(), 'utf-8')
      except UnicodeDecodeError:
        pass
    except URLError, e:
      print "Cannot send exception: %s" % e.reason
 
crashkit = None

def initialize_crashkit(account_name, product_name):
  global crashkit
  crashkit = CrashKit(account_name, product_name)
  
def send_exception(data = {}, env = {}):
  crashkit.send_exception(data, env)
 
def get_traceback(tb):
  traceback = []
  while tb != None:
    traceback.append(tb)
    tb = tb.tb_next
  traceback.reverse()
  return traceback

def get_class_name(frame):
  code = frame.f_code
  fname = code.co_name
  if code.co_argcount > 0:
    first = code.co_varnames[0]
    self = frame.f_locals[first]
    for key in dir(self):
      attr = getattr(self, key, None)
      if attr is not None:
        try:
          fc = attr.im_func.func_code
          if fc == code:
            if isinstance(self, ClassType) or isinstance(self, type):
              return self.__name__
            else:
              return attr.im_class.__name__
        except AttributeError:
          pass
  return None

def encode_location(traceback):
  frame = traceback.tb_frame
  co = frame.f_code
  filename, lineno, name = co.co_filename, traceback.tb_lineno, co.co_name
  for folder in sys.path:
    if not folder.endswith('/'):
      folder += '/'
    if filename.startswith(folder):
      filename = filename[len(folder):]
      break
  # if filename.endswith('.py'):
  #   filename = filename[0:-3]
  result = { "file": filename, "method": name, "line": lineno }
  class_name = get_class_name(frame)
  if class_name:
    result['class'] = class_name
  return result

def encode_exception_name(exc):
  m = exc.__module__
  c = exc.__name__
  if m == '__main__' or m == 'exceptions':
    return c
  else:
    return '%s.%s' % (m, c)

def collect_platform_info():
  import platform
  env = {}
  env['os_kernel_name'] = platform.system()
  env['os_kernel_version'] = platform.release()
  if 'Linux' == platform.system():
    env['os_dist'] = ' '.join(platform.dist()).strip()
  env['cpu_arch'] = platform.architecture()[0]
  env['cpu_type'] = platform.processor()
  env['python_version'] = platform.python_version()
  return env
  
