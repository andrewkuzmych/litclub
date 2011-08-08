# -*- coding: utf-8 -*-
from djlib.simpleconfig.models import SimpleConfig

def set(name,value):
  try:
    conf = SimpleConfig.objects.get(name=name)
  except:
    conf = SimpleConfig(name=name)
  conf.value = value
  conf.save()

def get(name):
  try:
    conf = SimpleConfig.objects.get(name=name)
    return conf.value
  except:
    return None