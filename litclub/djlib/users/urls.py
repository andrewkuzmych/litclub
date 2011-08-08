# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('djlib.users.views',    
    (r'^logout_do/$', 'logout_do'),
    (r'^login_do/$', 'login_do'),
    (r'^login/$', 'login'),
    (r'^register/$', 'register'),
    (r'^register_ok/$', 'register_ok'),
    (r'^change_password/$', 'change_password'),
    (r'^profile/(.+?)/$', 'profile'),
    (r'^change_profile/$', 'change_profile'),
    (r'^change_userpic/$', 'change_userpic'),
)