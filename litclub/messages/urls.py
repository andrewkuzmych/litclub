# coding=utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('litclub.messages.views',
                            (r'^send/form/(.+?)/$', 'send_form'),
                            (r'^send/do', 'send_do'),

                            (r'^topics', 'topics'),
                            (r'^topic/(\d+)/$', 'topic'),
                            (r'^reply/do', 'reply'),

                            (r'^spam/send/form', 'send_spam_form'),
                            (r'^spam/send/do', 'send_spam_do'),
                       )