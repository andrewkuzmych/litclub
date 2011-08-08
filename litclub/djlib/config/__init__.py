# -*- coding: utf-8 -*-
from djlib.config.models import Config

import pickle

def set(name,value):
  try:
    conf = Config.objects.get(name=name)
  except:
    conf = Config(name=name)
  conf.value = pickle.dumps(value)
  conf.save()

def get(name):
  try:
    conf = Config.objects.get(name=name)
    return pickle.loads(conf.value)
  except:
    return None