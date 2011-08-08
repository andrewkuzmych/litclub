# -*- coding: utf-8 -*-

from litclub.texts.models import *
from django.contrib.syndication.feeds import Feed

class TextsFeed(Feed):
    title = u"Нові твори на Літклубі"
    link = u"/"

    def items(self):
        return Text.objects.filter(type__in=[1,2,3]).order_by('-submit_date')[:15]
       
           
class ForumFeed(Feed):
    title = u"Нові теми на форумі Літклубу"
    link = u"/"

    def items(self):
        return Text.objects.filter(type=4).order_by('-submit_date')[:15]