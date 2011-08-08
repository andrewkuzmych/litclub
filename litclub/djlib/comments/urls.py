# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',    
    (r'^add/$', 'djlib.comments.views.add_comment'),
    (r'^delete/(\d+)/$', 'djlib.comments.views.delete_comment'),
  )