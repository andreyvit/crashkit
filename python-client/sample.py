
import crashkit
crashkit.initialize_crashkit('test', 'py')

import re

def zoo(self, a, b):
  return a(b)

def poo(a, b):
  return Boo().tiger(a, b)
  
class Boo:
  
  def moo(self, a):
    a.match("#$%^&*([[[[[[)", "a")
    
  @staticmethod
  def smoo(a, b):
    c = Boo()
    c.oop = poo
    return c.oop(a, b)
  
  @classmethod
  def cmoo(klass, a, b):
    return Boo.smoo(a, b)
    
Boo.tiger = zoo


def mpoo(a, b):
  return Moo().tiger(a, b)
  
class Moo(object):
  
  def moo(self, a):
    Boo.cmoo(Boo().moo, a)
    
  @staticmethod
  def smoo(a, b):
    c = Moo()
    c.oop = mpoo
    return c.oop(a, b)
  
  @classmethod
  def cmoo(klass, a, b):
    return Moo.smoo(a, b)
    
Moo.tiger = zoo

def main():
  x = {}
  try:
    Moo.cmoo(Moo().moo, re)
  except Exception, e:
    crashkit.send_exception()
  
main()
