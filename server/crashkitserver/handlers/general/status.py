# -*- coding: utf-8
from crashkitserver.handlers.common import BaseHandler
from models import Report

class StatusHandler(BaseHandler):
  
  def get(self):
    queued_reports = Report.all().filter('status', 0).count()
    self.queued = queued_reports
    self.render_and_finish('system_status.html')
    
  def post(self):
    1 / 0

url_mapping = (
  ('/status/', StatusHandler),
)
