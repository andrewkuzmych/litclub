# coding=utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('litclub.users.views',
                       (r'^logout_do/$', 'logout_do'),
                       (r'^login_do/$', 'login_do'),
                       (r'^login/$', 'login'),
                       (r'^register/$', 'register'),
                       (r'^register_ok/$', 'register_ok'),
                       (r'^change_password/$', 'change_password'),
                       (r'^profile/(.+?)/$', 'profile'),
                       (r'^change_profile/$', 'change_profile'),
                       (r'^change_userpic/$', 'change_userpic'),

                       (r'^reset_password/$', 'reset_password'),
                       (r'^reset_password_set/$', 'reset_password_set'),
                       (r'^delete_user/(.+?)/$', 'delete_user'),

                       (r'^subscribe/(\d+)/$', 'subscribe'),
                       (r'^unsubscribe/(\d+)/$', 'unsubscribe'),
                       (r'^subscription/$', 'subscription_own'),
                       (r'^subscription/(\d+)/$', 'subscription_of'),

                       (r'^favorite/texts/$', 'favorite_texts_own'),
                       (r'^favorite/texts/(\d+)/$', 'favorite_texts'),
                       )