from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

def error(request,text):
  return render_to_response('users/error.html', { 'error': text }, context_instance=RequestContext(request))
  
import re
from operator import add
from time import time
from django.db import connection

import datetime

from django.conf import settings


def vars(request):
    return { 'MEDIA_URL': settings.MEDIA_URL, 'REFERER': request.META.get('HTTP_REFERER','') }

class TimeLogMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # time the view
        start = time()
        response = view_func(request, *view_args, **view_kwargs)
        totTime = time() - start
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""insert into `logs`.`stats_timelog` set site = 'litclub', url = %s, ip_address = %s,
          date = %s,
          time = %s,
          info = '';  
          """,
          [request.path, request.META['REMOTE_ADDR'], datetime.datetime.today(), totTime * 1000])
          
        return response
  