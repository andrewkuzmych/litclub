# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'(?P<sid>\w+).gif$','djlib.captcha.views.captcha_image'),
)

