
from crashkitserver.handlers.common import BaseHandler

class HomeHandler(BaseHandler):
  
  def get(self):
    self.render_and_finish('site_home.html')

url_mapping = (
  ('/', HomeHandler),
)
