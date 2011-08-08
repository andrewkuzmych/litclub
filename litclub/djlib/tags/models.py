# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType

class Tag(models.Model): 
    text = models.CharField(max_length=50,unique=True)

class ContentMap(models.Model): 
    contentType = models.ForeignKey(ContentType)
    objectID = models.IntegerField(db_index=True)
    tags = models.ManyToManyField(Tag) 



