
import os

def set_logged_in_user(email, admin=False):
  if email is None or email == '':
    email, domain = '', 'example.com'
    admin = False
  else:
    domain = email[email.index('@')+1:]
    
  os.environ['USER_EMAIL']  = email
  os.environ['AUTH_DOMAIN'] = domain
  os.environ['REMOTE_ADDR'] = '127.0.0.1'
  os.environ['USER_IS_ADMIN'] = ('1' if admin else '0')
  os.environ['SERVER_NAME'] = 'localhost'
  os.environ['SERVER_PORT'] = ''
  

class UserTestCase(object):
  
  def setUp(self):
    super(UserTestCase, self).setUp()
    if hasattr(self, 'ADMIN'):
      set_logged_in_user(self.ADMIN, admin=True)
    elif hasattr(self, 'USER'):
      set_logged_in_user(self.USER)
    else:
      set_logged_in_user(None)
      
  def tearDown(self):
    set_logged_in_user(None)
    super(UserTestCase, self).tearDown()
