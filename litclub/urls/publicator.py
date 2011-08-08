# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
#from litclub.urls.feeds import *
from django.conf import settings

#from litclub.users import models

#feeds = {
#    'texts': TextsFeed,
#    'forum': ForumFeed,
#}

urlpatterns = patterns('',
    (r'^$', 'litclub.texts.publicator.main'),
    (r'^users/', include('litclub.users.urls')),
    (r'^texts/(add)/', 'litclub.texts.views.modify_text_publicator'),
    (r'^texts/(change)/(\d+)/', 'litclub.texts.views.modify_text_publicator'),
    (r'^texts/', include('litclub.texts.urls')),
    (r'^comments/', include('djlib.comments.urls')),
    
    (r'^admin/', include('django.contrib.admin.urls')),
    #(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    
    (r'^captcha/', include('djlib.captcha.urls')),
    
    (r'^users/list/$', 'litclub.users.views.list'),
    
    # Щоб працювали старі урли
    (r'^pub/$', 'litclub.texts.publicator.main'),
    (r'^pub/[^/]+/(\d+)/$', 'litclub.texts.views.show_text'),
    (r'^pub/[^/]+/(\d+)/comment/$', 'litclub.texts.views.show_text'),
    (r'^pub/([^/]+)/$', 'litclub.users.views.profile'),
    (r'^pub/([^/]+)/details', 'litclub.users.views.profile'),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^files/(.*)$', 'django.views.static.serve', {'document_root': '/sites/litclub/media/publicator'}), 
#        (r'^files/(.*)$', 'django.views.static.serve', {'document_root': '/home/nelyud/trunk/media/publicator'}), 
    )
