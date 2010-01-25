
__all__ = ['reltime']

from datetime import date, datetime, timedelta

def reldate(value):
  today = date.today()
  value = date(value.year, value.month, value.day)
  delta = timedelta(days=1)
  if value >= today:
    return 'today'
  elif value == today - delta:
    return 'yesterday'
  else:
    delta = today - value
    return '%d days old' % delta.days

def reltime(value):
  now = datetime.now()
  delta = now - value
  if delta >= timedelta(days=1):
    return reldate(value)
  elif delta >= timedelta(hours=1):
    return "%d hours ago" % delta.seconds / timedelta(hours=1).seconds
  elif delta >= timedelta(minutes=1):
    return "%d minutes ago" % delta.seconds / timedelta(minutes=1).seconds
  else:
    return "just now"
