# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
#from litclub.urls.feeds import *
from django.conf import settings
#from litclub.users import models

"""
feeds = {
    'texts': TextsFeed,
    'forum': ForumFeed,
}
"""

urlpatterns = patterns('',
    (r'^$', 'litclub.texts.views.main'),
    (r'^users/', include('litclub.users.urls')),
    (r'^texts/', include('litclub.texts.urls')),
    (r'^messages/', include('litclub.messages.urls')),
    (r'^comments/', include('djlib.comments.urls')),
    
    (r'^admin/', include('django.contrib.admin.urls')),
    #(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    
    (r'^captcha/', include('djlib.captcha.urls')),
    
    (r'^users/list/$', 'litclub.users.views.list')

    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^files/(.*)$', 'django.views.static.serve', {'document_root': '/sites/litclub/media/litclub'}), 
    )