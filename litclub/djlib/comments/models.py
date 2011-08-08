# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class Comment(models.Model): 
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(db_index=True)
    user = models.ForeignKey(User, null=True)
    
    usertype = models.IntegerField(default=1) # Тип користувача. 1 - з бази, 2 - анонімний
    name = models.CharField(max_length=60, blank=True, null=True) # Ім'я. Для анонімних
    email = models.CharField(max_length=60, blank=True, null=True) # E-mail. Для анонімних
    
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    comment = models.TextField()
    submit_date = models.DateTimeField(auto_now_add=True,db_index=True)
    ip_address = models.IPAddressField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    rating = models.IntegerField(default=0,blank=True)
