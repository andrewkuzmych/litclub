# -*- coding: utf-8 -*-
from django.db import models

class Config(models.Model): 
    name = models.CharField(max_length=255,db_index=True,unique=True)
    value = models.TextField()