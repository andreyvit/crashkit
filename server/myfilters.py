# -*- coding: utf-8
import datetime
import os
import re
from google.appengine.ext.webapp import template

register = template.create_template_register()

@register.filter
def errorspan(error):
  if error:
    return """ <span class="error">%s</span> """ % error
  else:
    return ""

@register.filter
def ifnone(value, subst = ''):
  if value == None:
    return subst
  else:
    return value

@register.filter
def selectedifeq(value, sample):
  if str(value) == str(sample):
    return """ selected="selected" """
  else:
    return ""

@register.filter
def checkediftrue(value):
  if value:
    return """ checked="checked" """
  else:
    return ""

@register.filter
def kgetattr(value, key):
  try:
    return getattr(value, key)
  except AttributeError:
    return ''
  
@register.filter
def strip_prefix(value, prefix):
  if value.startswith(prefix):
    return value[len(prefix):]
  else:
    return value
  
@register.filter
def shorten(value, l):
  if len(value) > l:
    return u"…" + value[-l+1:]
  else:
    return value
  
@register.filter
def unshortened_tooltip(value, l):
  if len(value) > l:
    return value
  else:
    return ''
    
@register.filter
def split_klass(value):
  pos = value.find('$')
  if pos < 0:
    return value
  else:
    outer, inner = value[0:pos], value[pos:]
    return "%s<small>%s</small>" % (outer, inner)
    
@register.filter
def scalenum(value):
  if value >= 1000:
    return """<span class="dig4">%d</span>""" % value
  if value >= 100:
    return """<span class="dig3">%d</span>""" % value
  return value
  
def shorten_fragment(o):
  if len(o) < 5:
    return o
  suffix_len = 2
  if o.endswith('ion') or o.endswith('ing'):
    suffix_len = 3
  prefix, mid, suffix = o[0:2], o[2:-suffix_len], o[-suffix_len:]
  result = prefix + re.sub('[euioa]', '', mid) + suffix
  if len(result) == len(o) - 1 and not re.search('[euioa]', prefix):
    return o  # removing just one letter is a bad choice
  return result
  
@register.filter
def smartshorten(s, target_len):
    
  def repl2(o):
    return shorten_fragment(o.group(0))
  
  def repl(o):
    o = o.group(0)
    if re.search('[A-Z]', o):
      return re.sub('(?:^|[A-Z])[a-z]*', repl2, o)
    else:
      return shorten_fragment(o)
      
  if len(s) <= target_len:
    return s
  result = re.sub('[a-zA-Z]+', repl, s)
  if len(result) > target_len:
    result = result[0:target_len]
  return result

@register.filter
def naturalday(value, fmt = '%A'):
  today = datetime.date.today()
  try:
    value = datetime.date(value.year, value.month, value.day)
  except Exception, e:
    return "%s" % e.__class__.__name__ 
  delta = datetime.timedelta(days=1)
  if value == today:
      return 'today'
  elif value == today + delta:
      return 'tomorrow'
  elif value == today - delta:
      return 'yesterday'
  return value.strftime(fmt.replace('_', ' '))

@register.filter
def daysold(value):
  today = datetime.date.today()
  value = datetime.date(value.year, value.month, value.day)
  delta = datetime.timedelta(days=1)
  if value >= today:
    return 'today'
  elif value == today - delta:
    return 'yesterday'
  else:
    delta = today - value
    return '%d days old' % delta
  
# register.filter(time_delta_in_words)
