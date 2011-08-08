# -*- coding: utf-8 -*-

from djlib.tags.models import ContentMap, Tag
from django.contrib.contenttypes.models import ContentType

import pickle

def _getCT(ct):
  app_label, model = ct.split('.')
  return ContentType.objects.get(app_label=app_label, model=model)
  
def addForObject(object_id,ct,tags):
  tags = tags.split(',')
  tags = dict([(item, None) for item in tags]).keys() # усуває дублікати
  
  content_type = _getCT(ct)
  try:
    obj = ContentMap.objects.get(contentType=content_type, objectID=object_id)      
  except:
    obj = ContentMap(contentType=content_type, objectID=object_id)
    obj.save()
  
  for tag in obj.tags.all():
    if tag.contentmap_set.all().count() < 2:
      tag.delete()
  obj.tags.clear()
  
  o_tags = []
  for t in tags:
    if t and t.strip():
      t = t.strip()
      try:
        tag = Tag.objects.get(text=t)
      except:
        tag = Tag(text=t)
        tag.save()
      o_tags.append(tag)
  
  for t in o_tags:
    obj.tags.add(t)
  obj.save()
  return pickle.dumps(o_tags)
  # obj = pickle.loads(ser)

def get(object_id,ct,ser_tags=""):
  if ser_tags:
    return pickle.loads(str(ser_tags))
 
  content_type = _getCT(ct)
  try:
    obj = ContentMap.objects.get(contentType=content_type, objectID=object_id)
    return obj.tags.all()
  except:
    return []


def delete(object_id,ct):
  content_type = _getCT(ct)
  #try:
  if 1:
    obj = ContentMap.objects.get(contentType=content_type, objectID=object_id)
    for tag in obj.tags.all():
      if tag.contentmap_set.all().count() < 2:
        tag.delete()
    obj.delete()
  #except:
  #  pass


def objects(tags,ct):
  content_type = _getCT(ct)
  tags = tags.split('+')
  o_tags = Tag.objects.filter(text__in=tags)
  return [ item.objectID for item in ContentMap.objects.filter(contentType=content_type,tags__in=o_tags).distinct()]
  
  
def cloud(exclude=['0']):
  font_min = 9
  font_max = 28
  
  n_min = 0
  n_max = 0
  
  from django.db import connection
  cursor = connection.cursor()
  cursor.execute("select t.text, count(*) as c from tags_contentmap_tags as m left join tags_tag as t on m.tag_id = t.id where not t.id in (%s) group by tag_id order by c desc limit 10" % ','.join(exclude))
  tags = list(cursor.fetchall())
  if tags:
    n_min = min([ int(t[1]) for t in tags ])
    n_max = max([ int(t[1]) for t in tags ])
  
  if not n_max - n_min == 0:
    step = float(font_max - font_min)/float(n_max - n_min)
  else:
    step = 0
  
  ret_tags = []
  for t in tags:
    ret_tags.append( [t[0], t[1], int( font_min + (t[1] - n_min) * step), None] )
  for t in ret_tags:
    t[3] = unicode( hex(180-int(180.0/(font_max - font_min) * (t[2] - font_min))) ).replace('0x', '') * 3
  
  ret_tags.sort(lambda x, y: cmp(x[0].lower(), y[0].lower()))
  return ret_tags
