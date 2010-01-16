
import unittest
import pexpect
import urllib2
import os
import sys
import json
import re
import difflib

CRASHKIT_HOST = "localhost:5005"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_DIR = os.path.join(BASE_DIR, 'python-client')
ENV = {'CRASHKIT_HOST': CRASHKIT_HOST}
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expected-reports')

class CrashKitClientTestCase(unittest.TestCase):
  
  def assertMatches(self, regexp, text):
    self.assertTrue(re.match(regexp, text), "Text does not match RE %s:\n%s\n" % (regexp, text))
  
  def assertTextEqual(self, expected, actual):
    if expected != actual:
      self.assertTrue(False, "Not equal:\n" + "\n".join([line for line in difflib.unified_diff(expected.split("\n"), actual.split("\n"), fromfile="expected.json", tofile="actual.json")]))
    else:
      self.assertTrue(True)
    
  def assertJsonEqual(self, expected, actual):
    self.assertTextEqual(json.dumps(expected, sort_keys=True, indent=4), json.dumps(actual, sort_keys=True, indent=4))
  
  pass
  
def normalize_report(report):
  report = report[:]
  for occur in report:
    if 'client_version' in occur:
      del occur['client_version']
  
    for exc in occur.get('exceptions', []):
      for loc in exc.get('locations', []):
        if 'file' in loc:
          loc['file'] = os.path.basename(loc['file'])
  return report
  
class PythonClientTestCase(CrashKitClientTestCase):
  
  def test_regular_python(self):
    child = pexpect.spawn('python', [os.path.join(PYTHON_DIR, 'sample.py')], env=ENV)
    child.logfile = sys.stdout
    child.expect(pexpect.EOF)
    
    body = urllib2.urlopen('http://%s/test/products/py/last-posted-report' % CRASHKIT_HOST).read()
    body = json.loads(body)
    
    self.assertEqual(1, len(body))
    self.assertMatches('{{ver}}|[0-9.]+', body[0].get('client_version', ''))

    body = normalize_report(body)
    expected = normalize_report(json.loads(file(os.path.join(REPORTS_DIR, 'python.json')).read()))
    self.assertJsonEqual(expected, body)

if __name__ == '__main__':
  unittest.main()
