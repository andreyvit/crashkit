# -*- coding: utf-8
from unittest import TestCase
from gaetestbed import UnitTestCase, FunctionalTestCase
from main import application

class ErrorPagesTestCase(FunctionalTestCase, TestCase):
  APPLICATION = application

  def test_404(self):
    response = self.get('/qwerty/', status=404)
    assert '<h2>Page Does Not Exist</h2>' in str(response)

  def test_500(self):
    response = self.get('/simulate-error/500/', status=500)
    assert '<h2>Internal Server Error</h2>' in str(response)

  def test_403(self):
    response = self.get('/simulate-error/403/', status=403)
    assert '<h2>Access Denied</h2>' in str(response)

  def test_400(self):
    response = self.get('/simulate-error/400/', status=400)
    assert '<h2>Bad Request</h2>' in str(response)
