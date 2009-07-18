#! /usr/bin/python

import getopt
import urlparse
import os
import sys
import time
from getpass import getpass

try:
  import yaml
except ImportError:
  print 'Please download PyYAML from http://pyyaml.org/wiki/PyYAML.'
  sys.exit(1)

APPENGINE_PATH = '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/'
sys.path = [
  APPENGINE_PATH,
  os.path.join(APPENGINE_PATH, 'lib', 'antlr3'),
  os.path.join(APPENGINE_PATH, 'lib', 'django'),
  os.path.join(APPENGINE_PATH, 'lib', 'webob'),
  os.path.join(APPENGINE_PATH, 'lib', 'yaml', 'lib'),
] + sys.path

from google.appengine.api import datastore_errors
from google.appengine.ext import db
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.runtime import apiproxy_errors
from google.appengine.tools import appengine_rpc

class expando(object):
  pass
  
config = expando()
config.appid = None
config.url = None
config.host = None
config.email = None
config.passin = False
config.batch_size = 10
config.sleep = 200
config.limit = None
config.only = None
config.ref = ''
config.text = ''
config.test = False

def Authenticate(self):
  """Invoke authentication if necessary."""
  logger.info('Connecting to %s', self.url_path)
  self.rpc_server.Send(self.url_path, payload=None)
  self.authenticated = True

def provide_credentials():
  if not config.email:
    print 'Please enter login credentials for %s.' % config.host
    config.email = raw_input('Email: ')

  return (config.email, 'Supreme29court')
  if config.email:
    password_prompt = 'Password for %s: ' % config.email
    if config.passin:
      config.password = raw_input(password_prompt)
    else:
      config.password = getpass(password_prompt)
  else:
    config.password = None

  return (config.email, config.password)

def define_model(kind):
  return type(kind, (db.Expando,), {})

def preprocess(v):
  if isinstance(v, long):
    v = int(v)
  elif isinstance(v, db.Key):
    v = v.kind() + '/' + str(v.id_or_name())
  elif isinstance(v, db.Text):
    v = unicode(v)
  elif isinstance(v, (list, tuple)):
    v = [preprocess(e) for e in v]
  if isinstance(v, unicode):
    v = v.encode('utf-8')
  return v
  
def convert(item):
  data = dict()
  for k, v in item._dynamic_properties.iteritems():
    if config.only and k not in config.only: continue
    data[k] = preprocess(v)
  key = preprocess(item.key())
  return { key: data }
  
def decode_key(key_str):
  kind, id_or_name = key_str.split('/', 1)
  try:
    id_or_name = int(id_or_name)
    id_or_name = 'IMP%d' % id_or_name
  except ValueError:
    pass
  return db.Key.from_path(kind, id_or_name)
  
def decode_attr(key, value):
  if isinstance(value, str):
    value = unicode(value, 'utf-8')
  if key in config.ref:
    value = decode_key(value)
  elif key in config.text:
    value = db.Text(value)
  return value
  
def decode_attrs(attrs):
  result = {}
  for key, value in attrs.iteritems():
    if isinstance(value, (tuple,list)):
      value = [decode_attr(key, v) for v in value]
    else:
      value = decode_attr(key, value)
    result[key] = value
  return result
  
def run_upload_for_file(input_file, index, count, models):
  print "Uploading %s (%d of %d)..." % (os.path.basename(input_file), index+1, count)
  items = yaml.load(open(input_file).read())
  for key_value_pair in items:
    assert len(key_value_pair) == 1
    for key, item in key_value_pair.iteritems():
      key   = decode_key(key)
      item  = decode_attrs(item)
      kind  = str(key.kind())
      model = models.get(kind)
      if model is None:
        models[kind] = model = define_model(kind)
      
      if config.test:
        print repr(key)
        for k, v in item.iteritems():
          print '%-20s %s' % (k, v)
        return
      else:
        # print dir(model)
        # return
        row = model(key_name=key.name(), parent=key.parent())
        for k, v in item.iteritems():
          setattr(row, k, v)
        row.put()

def run_upload(input_files):
  models = {}
  index = 0
  for input_file in input_files:
    run_upload_for_file(input_file, index, len(input_files), models)
    index += 1
  
class MultiFileOutput(object):
  def __init__(self, file_name, rows_per_file):
    self.basename, self.ext = os.path.splitext(file_name)
    self.file = None
    self.index = 1
    self.rows_per_file = rows_per_file
    self.per_file_count = 0
    
  def file_name(self):
    return '%s%04d%s' % (self.basename, self.index, self.ext)
    
  def opened_file(self):
    if self.file is None:
      self.file = open(self.file_name(), 'w')
    return self.file
      
  def write_chunk(self, count, data):
    print >>self.opened_file(), data
    self.per_file_count += count
    if self.per_file_count >= self.per_file_count:
      self.close()
    else:
      self.file.flush()
      
  def close(self):
    if self.file:
      self.file.close()
      self.file = None
      self.index += 1
      self.per_file_count = 0
  
def run_download(output_file, models):
  last_key = None
  count = 0
  file_index = 1
  output = MultiFileOutput(output_file, config.rows_per_file or 1000)
  
  for model in models:
    print 'Downloading %s of kind %s from %s into %s (batch size %d, sleep %s ms).' % (
        'all rows' if config.limit is None else 'up to %d rows' % config.limit,
        model.kind(), config.host_port, output.file_name(),
        config.batch_size, config.sleep)

    if config.rows_per_file:
      output.close()
      
    done = 0
    while True:
      query = model.all()
      if last_key:
        query.filter('__key__ >', last_key)
      items = query.fetch(min(config.batch_size, config.limit-done) if config.limit else config.batch_size)
      if len(items) == 0: break
    
      converted = [convert(item) for item in items]
      output.write_chunk(len(items), yaml.dump(converted, indent=2, default_flow_style=False))
      
      done += len(items)
      last_key = items[-1].key()
      print '%d entities done so far, up to key %s' % (done, preprocess(last_key))
      time.sleep(config.sleep / 1000.0)
      
      if config.limit and done >= config.limit: break
    
  output.close()
  
def usage():
  print 'Usage:'
  print '  %s [options] download http://appid.appspot.com/remote_api entities.yml MyEntityKind MyAnotherKind' % os.path.basename(sys.argv[0])
  print '  %s [options] upload   http://appid.appspot.com/remote_api entities.yml more_entities.yml' % os.path.basename(sys.argv[0])
  print
  print 'Common options:'
  print '   --passin                       read password from stdin'
  print '   --email=you@domain.com         Google Account to use for authentication (will ask if not given)'
  print '   --appid=coolapp                app id (required if using a custom domain in URL)'
  print '   --limit=5000                   stop after downloading/uploading this many items (useful for testing)'
  print '   --batch-size=10                download/upload this many items in one Datastore request'
  print '   --sleep=200                    sleep this many milliseconds after downloading/uploading each batch'
  print
  print 'Download options:'
  print '   --rows-per-file=1000           save output to multiple sequentially numbered files'
  print
  print 'Upload options:'
  print '   --test                         output the first row of each file as it would be uploaded (no actual upload happens)'
  print '   --ref=foo,bar,boz              treat the given fields as references (otherwise will be uploaded as strings)'
  print '   --text=foo,bar,boz             treat the given fields as db.Text (otherwise will be uploaded as strings)'
  
  sys.exit(13)

def main():
  opts, unused_args = getopt.getopt(sys.argv[1:], 'h', ['passin', 'email=', 'appid=', 'batch-size=', 'sleep=', 'limit=', 'only=', 'ref=', 'text=', 'test', 'rows-per-file='])
  if len(unused_args) < 3: usage()
  command        = unused_args.pop(0)
  remote_api_url = unused_args.pop(0)
  
  if command not in ('upload', 'download'): usage()
  if command == 'download':
    output_file = unused_args.pop(0)
    entity_kinds = unused_args
    models = [define_model(kind) for kind in entity_kinds]
    def run_handler():
      run_download(output_file, models)
  else:
    input_files = unused_args
    def run_handler():
      run_upload(input_files)
  
  handler = globals()['run_' + command]
  
  for k, v in opts:
    if k.startswith('--'): k = k[2:]
    if v == '': v = True
    setattr(config, k.replace('-', '_'), v)
  
  (scheme, host_port, remote_api_path, unused_query, unused_fragment) = urlparse.urlsplit(remote_api_url)
  host = host_port.split(':')[0]

  if config.appid:
    appid = config.appid
  elif host.endswith('.appspot.com'):
    appid = host.split('.')[-3]
  elif host.endswith('google.com'):
    appid = host.split('.')[0]
  else:
    print 'Cannot deduce app id from URL, please specify --appid=your-app-id.'
    sys.exit(13)

  remote_api_stub.ConfigureRemoteDatastore(appid, remote_api_path, provide_credentials,
      servername=host_port, secure=(scheme == 'https'))
      
  config.ref = config.ref.split(',')
  config.text = config.text.split(',')
      
  config.host = host
  config.host_port = host_port
  config.batch_size = int(config.batch_size)
  config.sleep = int(config.sleep)
  if config.limit: config.limit = int(config.limit)
  if config.only:  config.only = config.only.split(',')
  
  run_handler()

if __name__ == '__main__':
  main()
