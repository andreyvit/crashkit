import string
from random import Random

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

# def group(seq):
#     '''seq is a sequence of tuple containing (item_to_be_categorized, category)'''
#     result = {}
#     for item, category in seq:
#         result.setdefault(category, []).append(item)
#     return result 
