# -*- coding: utf-8
from unittest import TestCase
from gaetestbed import UnitTestCase, FunctionalTestCase
from fixture import DataTestCase
from usertestcase import UserTestCase
from main import application

from models import LimitedBetaCandidate
from testingdata import the_gae_fixture, AccountData, LimitedBetaCandidateData, ServerConfigData, admin_user

class LimitedBetaSignup(FunctionalTestCase, TestCase):
  APPLICATION = application
  
  def test_signup(self):
    fix = LimitedBetaCandidateData.acmeceo_uninvited
    response = self.post('/betasignup/', {'email': fix.email, 'tech': fix.tech})
    assert 'Thanks a lot!' in str(response)

    cc = LimitedBetaCandidate.all().fetch(100)
    assert len(cc) == 1
    assert cc[0].email == fix.email
    assert cc[0].tech == fix.tech


class LimitedBetaInvitation(DataTestCase, UserTestCase, FunctionalTestCase, TestCase):
  APPLICATION = application
  fixture     = the_gae_fixture
  datasets = (LimitedBetaCandidateData,ServerConfigData)
  ADMIN = admin_user
  
  def test_list_candidates(self):
    response = self.get('/admin/beta/')
    assert LimitedBetaCandidateData.acmeceo_uninvited.email in str(response)
  
  def test_invite(self):
    response = self.get('/admin/beta/accept', {'key': LimitedBetaCandidateData.acmeceo_uninvited_obj.key()})
    self.assertRedirects(response, to='/admin/beta/')
    self.assertEmailSent(to=LimitedBetaCandidateData.acmeceo_uninvited.email)

