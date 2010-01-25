# -*- coding: utf-8
from unittest import TestCase
from gaetestbed import UnitTestCase, FunctionalTestCase
from main import application

class MarketingSiteTestCase(FunctionalTestCase, TestCase):
  APPLICATION = application

  def test_homepage(self):
    response = self.get('/')
    assert 'Exception-driven development' in str(response)
