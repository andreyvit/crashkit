# -*- coding: utf-8
from datetime import datetime, timedelta
import time
import logging
import wsgiref.handlers
import os
import string
import urllib
import sets
from random import Random
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from django.utils import simplejson as json
from models import *
from processor import process_report, process_case

from controllers.base import *

class SignUpForLimitedBetaHandler(BaseHandler):
  
  @prolog()
  def post(self):
    email = self.request.get('email')
    tech  = self.request.get('tech')
    if tech == None:
      tech = ''
    pers = LimitedBetaCandidate(email=email, tech=tech)
    pers.put()
    
    body = """
Hey buddies,

Another lucky person has signed up for our Feedback Kit limited beta program.

His/her e-mail address:  %s
He/she is interested in: %s
""" % (email, tech)
    mail.send_mail_to_admins('andreyvit@gmail.com', '[Feedback Kit] New Limited Beta User', body)
    
    self.response.out.write("Thanks a lot! We'll e-mail you an invitation code soon.")

class LimitedBetaCandidateListHandler(BaseHandler):
  @prolog(check = ['is_server_management_allowed'])
  def get(self):
    candidates = LimitedBetaCandidate.all().filter('invitation_code', None).filter('rejected', False).order('created_at').fetch(100)
    self.data.update(candidates=candidates)
    self.render_and_finish('beta_candidates.html')

class LimitedBetaAcceptCandidateHandler(BaseHandler):
  @prolog(check = ['is_server_management_allowed'])
  def get(self):
    key = self.request.get('key')
    candidate = LimitedBetaCandidate.get(key)
    candidate.invitation_code = random_string()
    candidate.put()
    
    body = """
Dear %(email)s,

Once upon a time you have left us your e-mail address asking
to participate in the limited beta program of YourSway Feedback Kit. 

We are glad to accept you today!

Please use the following link to sign up for an account.

  http://%(host)s/signup/%(code)s
    
""" % dict(email=candidate.email, host=self.request.host, code=candidate.invitation_code)

    mail.send_mail('andreyvit@gmail.com', candidate.email, 'YourSway Feedback Kit limited beta', body)
    
    self.redirect_and_finish('/beta/', flash = "Accepted %s." % candidate.email)

class LimitedBetaRejectCandidateHandler(BaseHandler):
  @prolog(check = ['is_server_management_allowed'])
  def get(self):
    key = self.request.get('key')
    candidate = LimitedBetaCandidate.get(key)
    candidate.rejected = True
    candidate.put()
    self.redirect_and_finish('/beta/', flash = "Rejected %s." % candidate.email)
