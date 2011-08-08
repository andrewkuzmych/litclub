# -*- coding: utf-8 -*-
from django.db import models

class SimpleConfig(models.Model): 
    name = models.CharField(max_length=255,db_index=True,unique=True)
    value = models.TextField()
    
    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"
        
    class Admin:
        pass
        
    def __str__(self):
        return self.name