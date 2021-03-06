# -*- coding: utf-8
from google.appengine.api import users, memcache, mail
from google.appengine.ext import db

from crashkitserver.handlers.common import WebHandler
from models import ServerConfig, LimitedBetaCandidate
from yoursway.utils.stringutil import random_string
from yoursway.gae.utils import requires_admin

def server_config():
    config = ServerConfig.get_by_key_name('TheConfig')
    if config is None:
        config = ServerConfig(key_name = 'TheConfig')
        config.signup_email_unused_text = """CrashKit limited beta invitation

Dear %(email)s,

Once upon a time you have left us your e-mail address asking
to participate in the limited beta program of YourSway CrashKit. 

We are glad to accept you today!

Please use the following link to sign up for an account.

  http://%(host)s/signup/%(code)s

If (or when) you find a bug or have something else to say,
just reply this e-mail. Any feedback is greatly appreciated.
"""
    return config

class SignUpForLimitedBetaHandler(WebHandler):
  
  def post(self):
    email = self.request.get('email')
    tech  = self.request.get('tech')
    if tech == None:
      tech = ''
    candidate = LimitedBetaCandidate(email=email, tech=tech)
    candidate.put()
    
    body = """
Hey buddies,

CrashKit limited beta program signup:

His/her e-mail address:  %(email)s
He/she is interested in: %(tech)s

Please visit http://%(host)s/admin/beta/ to invite this user.
""" % dict(email=candidate.email, host=self.request.host, tech=candidate.tech)
    mail.send_mail_to_admins('crashkit@yoursway.com', '[CrK] New Limited Beta User', body)
    
    self.response.out.write("Thanks a lot! We'll e-mail you an invitation code soon.")

class LimitedBetaCandidateListHandler(WebHandler):
  
  @requires_admin
  def get(self):
    self.server_config = server_config()
    self.render_editor_and_finish()
    
  def render_editor_and_finish(self):
    self.candidates = LimitedBetaCandidate.all().filter('invitation_code', None).filter('rejected', False).order('created_at').fetch(100)
    self.render_and_finish('beta_candidates.html')

  @requires_admin
  def post(self):
    self.server_config = server_config()
    
    self.server_config.signup_email_subject     = self.valid_string('signup_email_subject')
    self.server_config.signup_email_text        = self.valid_string('signup_email_text')
    self.server_config.signup_email_unused_text = self.valid_string('signup_email_unused_text', required=False)

    if not self.is_valid():
      self.render_editor_and_finish()
      
    self.server_config.put()
    self.redirect_and_finish('/admin/beta/', flash = "E-mail settings saved.")

class LimitedBetaAcceptCandidateHandler(WebHandler):
  
  @requires_admin
  def get(self):
    self.server_config = server_config()
    if self.server_config.signup_email_text is None or len(self.server_config.signup_email_text) == 0:
      self.redirect_and_finish('/admin/beta/', flash = "Please set up a email text before accepting people.")
      
    key = self.request.get('key')
    candidate = LimitedBetaCandidate.get(key)
    candidate.invitation_code = random_string()
    candidate.put()
    
    data = dict(email=candidate.email, host=self.request.host, code=candidate.invitation_code)
    body = self.server_config.signup_email_text % data
    subject = self.server_config.signup_email_subject % data

    mail.send_mail('crashkit@yoursway.com', candidate.email, subject, body)
    
    self.redirect_and_finish('/admin/beta/', flash = "Accepted %s, his invite code is %s." % (candidate.email, candidate.invitation_code))

class LimitedBetaRejectCandidateHandler(WebHandler):
  
  @requires_admin
  def get(self):
    key = self.request.get('key')
    candidate = LimitedBetaCandidate.get(key)
    candidate.rejected = True
    candidate.put()
    self.redirect_and_finish('/admin/beta/', flash = "Rejected %s." % candidate.email)

url_mapping = (
  ('/betasignup/', SignUpForLimitedBetaHandler),
  ('/admin/beta/', LimitedBetaCandidateListHandler),
  ('/admin/beta/accept', LimitedBetaAcceptCandidateHandler),
  ('/admin/beta/reject', LimitedBetaRejectCandidateHandler),
)
