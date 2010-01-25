# -*- coding: utf-8
from unittest import TestCase
from gaetestbed import UnitTestCase, FunctionalTestCase
from fixture import DataTestCase
from main import application

from models import Report, Client, REPORT_NEW, Product
from testingdata import the_gae_fixture, AccountData, ProductData

class StatusSiteTestCase(DataTestCase, FunctionalTestCase, TestCase):
  APPLICATION = application
  fixture = the_gae_fixture
  datasets = [AccountData, ProductData]
  
  def test_emptystatus(self):
    response = self.get('/status/')
    assert 'Queued Reports: 0' in str(response)

  def test_one_report(self):
    client = Client(product=ProductData.killerapp_obj, cookie='123')
    client.put()
    report = Report(product=ProductData.killerapp_obj, client=client, status=REPORT_NEW, remote_ip='127.0.0.1', data='[]')
    report.put()
  
    response = self.get('/status/')
    assert 'Queued Reports: 1' in str(response)
