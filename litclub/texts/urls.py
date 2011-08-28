from django.conf.urls.defaults import *
from litclub.texts.models import *

urlpatterns = patterns('',
                       (r'^add/([1-5])/$', 'litclub.texts.views.add_text'),
                       (r'^change/(\d+)/$', 'litclub.texts.views.change_text'),
                       (r'^delete/(\d+)/$', 'litclub.texts.views.delete_text'),
                       (r'^hide/(\d+)/$', 'litclub.texts.views.hide_text'),
                       (r'^show/(\d+)/$', 'litclub.texts.views.show_text'),
                       (r'^open/(\d+)/$', 'litclub.texts.views.open_text'),
                       (r'^list/([1-5])/$', 'litclub.texts.views.list_texts'),
                       (r'^list/$', 'litclub.texts.views.list_texts'),
                       #(r'^rating_count/$', 'litclub.texts.views.rating_count'),
                       (r'^favorite/add/(\d+)/$', 'litclub.texts.views.add_to_favorite'),
                       (r'^favorite/remove/(\d+)/$', 'litclub.texts.views.remove_from_favorite'),
                       )