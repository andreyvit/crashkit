# -*- coding: utf-8
import datetime
import os
import re
from google.appengine.ext.webapp import template

register = template.create_template_register()

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
