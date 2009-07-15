import string
from random import Random

import os
from google.appengine.api import users

def require_admin(handler_method):
  """Decorator that requires the requesting user to be an admin."""
  def decorate(myself, *args, **kwargs):
    if ('HTTP_X_APPENGINE_TASKNAME' in os.environ
        or users.is_current_user_admin()):
      handler_method(myself, *args, **kwargs)
    elif users.get_current_user() is None:
      myself.redirect(users.create_login_url(myself.request.url))
    else:
      myself.response.set_status(401)
  return decorate

def decline(num, one, many, zero=None):
  if   zero and num == 0:  fmt = zero
  elif one  and num == 1:  fmt = one
  else:                    fmt = many
  return fmt.replace('#', unicode(num))

def random_string(len = 12, chars = string.letters+string.digits):
  return ''.join(Random().sample(chars, 12))

def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    if not isinstance(html, unicode):
      if not isinstance(html, str):
        html = unicode(html)
      else:
        html = unicode(html, 'utf-8')
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def group(func, iterable):
    result = {}
    for i in iterable:
        result.setdefault(func(i), []).append(i) 
    return result
    
def index(func, iterable):
    result = {}
    for i in iterable:
        result[func(i)] = i
    return result
  
def flatten(l, ltypes=(list, tuple)):
  ltype = type(l)
  l = list(l)
  i = 0
  while i < len(l):
    while isinstance(l[i], ltypes):
      if not l[i]:
        l.pop(i)
        i -= 1
        break
      else:
        l[i:i + 1] = l[i]
    i += 1
  return ltype(l)

def date_to_week(d):
  iso_year, iso_week, iso_weekday = d.isocalendar()
  return iso_year * 100 + iso_week
  
def between(value, start, end):
  return value >= start and value <= end
  
def week_to_start_date(w):
  return iso_year_week_day_to_date(int(w / 100), w % 100, 1)
  
def week_to_end_date(w):
  return iso_year_week_day_to_date(int(w / 100), w % 100, 7)
  
def iso_year_week_day_to_date(y, w, d):
  from datetime import date, timedelta
  
  jan4 = date(y, 1, 4)
  jan4_monday_offset = jan4.weekday()
  if jan4_monday_offset == 0: jan4_monday_offset = 7
  
  result = jan4 + timedelta(days=(-jan4_monday_offset + 7*(w-1) + (d-1)))
  assert result.isocalendar() == (y, w, d)
  return result

def signum(int):
  if(int < 0): return -1
  elif(int > 0): return 1
  else: return 0

# def group(seq):
#     '''seq is a sequence of tuple containing (item_to_be_categorized, category)'''
#     result = {}
#     for item, category in seq:
#         result.setdefault(category, []).append(item)
#     return result 
