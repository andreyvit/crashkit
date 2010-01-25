
from crashkitserver.handlers.common import BaseHandler
from yoursway.web.handling import NotFound, AccessDenied, BadRequest

class FourOhFourHandler(BaseHandler):
  
  def get(self, path):
    raise NotFound, "Page not found at path: %s" % path

class FiveOhFiveHandler(BaseHandler):
  
  def get(self):
    1 / 0

class FourOhThreeHandler(BaseHandler):
  
  def get(self):
    raise AccessDenied, "Simulated access denial."

class FourOhOhHandler(BaseHandler):
  
  def get(self):
    raise BadRequest, "Simulated bad request error."

url_mapping = (
  ('/simulate-error/500/', FiveOhFiveHandler),
  ('/simulate-error/403/', FourOhThreeHandler),
  ('/simulate-error/400/', FourOhOhHandler),
  ('(.*)', FourOhFourHandler),
)
