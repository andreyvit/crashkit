
class ProcessReportHandler(BaseHandler):
  def post(self):
    report = Report.get_by_id(int(self.request.get('key')))
    if report.status != REPORT_NEW:
      return
    process_report(report)

url_mapping = (
  ('/qworkers/process-report', ProcessReportHandler),
)
