# coding=utf-8

from litclub.texts.models import *
from django import forms

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.db import connection
from litclub.users.models import *
from djlib.comments.models import *
from django.contrib.contenttypes.models import ContentType
import datetime
import re

from django.template import loader, Context
from django.core.mail import EmailMessage
from django.conf import settings

def main(request):
    texts = Text.objects.filter(type__in=[1, 2, 3, 5]).order_by('-submit_date')[:30]
    forum = Text.objects.filter(type=4).order_by('-submit_date')[:4]

    top = Text.objects.filter(type__in=[1, 2, 3, 5], rating__gt=0).order_by('-rating', '-submit_date', '-rating_count')[
          :40]
    week = Text.objects.filter(type__in=[1, 2, 3], rating__gt=0,
                               submit_date__gte=( datetime.date.today() - datetime.timedelta(days=7) )).order_by(
            '-rating', '-submit_date', '-rating_count')[:10]

    return render_to_response('main.html', {'texts': texts, 'forum': forum, 'top': top, 'week': week, },
                              context_instance=RequestContext(request))


def initpub():
    users = User.objects.all()
    for u in users:
        u.set_password(u.password)
        u.save()
        u.get_profile().count_texts();

    texts = Text.objects.all()
    cursor = connection.cursor()
    for text in texts:
        cursor.execute("SELECT count(*) FROM `comments_comment` WHERE `object_id` = '%s'" % text.id)
        row = cursor.fetchone()
        text.comments_count = row[0]
        try:
            c = Comment.objects.filter(object_id=text.id).order_by('-submit_date')[0]
            text.last_comment_date = c.submit_date
            text.last_comment_user = c.user
        except:
            pass
        text.save()
