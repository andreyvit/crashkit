# -*- coding: utf-8
from unittest import TestCase
from gaetestbed import UnitTestCase, FunctionalTestCase
from fixture import DataTestCase
from usertestcase import UserTestCase
from main import application

from models import LimitedBetaCandidate
from testingdata import the_gae_fixture, AccountData, LimitedBetaCandidateData, ServerConfigData, admin_user


class LimitedBetaAccountCreation(DataTestCase, UserTestCase, FunctionalTestCase, TestCase):
  APPLICATION = application
  fixture     = the_gae_fixture
  datasets = (LimitedBetaCandidateData,ServerConfigData)
  USER = LimitedBetaCandidateData.acmeceo_invited.email
  
  def test_signup(self):
    response = self.get('/signup/%s' % LimitedBetaCandidateData.acmeceo_invited.invitation_code)
    form = response.form
    form['name']      = AccountData.acme.name
    form['permalink'] = AccountData.acme.permalink
    response = form.submit()
    self.assertRedirects(response, to='/%s/products/new/' % AccountData.acme.permalink)
