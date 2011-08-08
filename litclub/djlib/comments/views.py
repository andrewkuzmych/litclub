# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from djlib.comments.models import Comment
from django.http import Http404, HttpResponseForbidden
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext 

from djlib.captcha.models import Captcha

from django.template import loader, Context

from django.conf import settings

from django.core.mail import EmailMessage 

import re

def _send_mail(*kw):
  try:
    msg = EmailMessage(*kw)
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()              	  
  except:
    pass

def add_comment(request):
  if not request.POST:
    raise Http404
  if request.POST.get('target','').find(':') < 0:
    raise Http404    
  
  # Перевірка Captcha
  if not request.user.is_authenticated():
    if not Captcha.validate(request.POST.get('captcha_sid',''),request.POST.get('captcha_text','')) == 1:
      form = request.POST
      sid = Captcha.new().sid
      return render_to_response('comments/captcha_failed_form.html', {'form': form, 'sid': sid }, context_instance=RequestContext(request))
  
  try: 
 
    # Об'єкт, який коментують
    (content_id, object_id) = request.POST['target'].split(':', 1)
    content_type = ContentType.objects.get(pk=int(content_id))
    obj = content_type.get_object_for_this_type(pk=int(object_id))
    comment = ''
    parent = None

    comment = request.POST['comment']
    parent = int(request.POST['parent']) or None
    if parent:
      parent = get_object_or_404(Comment,id=parent,object_id=obj.id,content_type=content_type)

    if comment:
      c = Comment(
        comment = comment,
        parent = parent,
        object_id = obj.id,
        content_type = content_type,
        ip_address = request.META['REMOTE_ADDR']
      )
      
      if re.search("litclub.{1,5}us", c.comment, re.I | re.M): return HttpResponseRedirect("/")
      
      if request.user.is_authenticated():
        c.user = request.user
        c.usertype = 1
      else:
        c.user = None
        c.usertype = 2
        c.name = request.POST.get('name','')
        c.email = request.POST.get('email','')
        
      c.save()
      
      # Якщо об'єкт вміє — встановити число коментарів та інформацію про останній
      try:
        obj.set_comments( c, Comment.objects.filter(content_type=content_type,object_id=obj.id,is_removed=False).count() )
      except:
        pass
      
      # Надіслати відповідь автору попереднього коментаря та автору тексту по пошті
      
      # Щоб можна було надсилати відповіді на коментарі анонімам
      if parent:
        if parent.user:
          parent.email = parent.user.email
          parent.name = parent.user.username
          
          # Якщо є настройка надсилання коментарів — використовавати їх, а інакше завжди надсилати
          try:
            if settings.COMMENTS_ALWAYS_SEND:
              parent.send_comments = 1
            else:
              parent.send_comments = parent.user.get_profile().comments
          except:
            parent.send_comments = 1
            
        else:
          parent.send_comments = 1
      
      obj_send_comments = 1
      try:
        obj_send_comments = obj.user.get_profile().comments
      except:
      	pass
      
      try:
        if settings.COMMENTS_ALWAYS_SEND: obj_send_comments = 1
      except: pass
        

      obj_user = obj.user
      try:
        if obj_user.user: obj_user = obj_user.user
      except: pass

      tpl = loader.get_template('comments/mail_reply.html')
      c_user = Context({
                   'comment': c,
                   'parent': parent,
                   'obj': obj,
                 })
      c_author = Context({
                   'comment': c,
                   'parent': parent,
                   'obj': obj,
                   'author': 1
                 })
      
      mail_subject_text = u"Коментар %s на Літклубі"
      mail_from = 'notify@litclub.org.ua'
      
      try:
        if settings.COMMENTS_MAIL_SUBJECT:
          mail_subject_text = settings.COMMENTS_MAIL_SUBJECT
      except:
        pass

      try:
        if settings.COMMENTS_MAIL_FROM:
          mail_from = settings.COMMENTS_MAIL_FROM
      except:
        pass

      
      if c.user:
        mail_title = mail_subject_text % c.user.username
      else:
        mail_title = mail_subject_text % c.name
        

      
      if parent:
        if c.user and c.user == obj_user:
          if c.user == parent.user:
            pass
          else:
            if parent.send_comments and parent.email:
              _send_mail(mail_title, tpl.render(c_user), mail_from, [parent.email])
        else:
          if c.user and c.user == parent.user:
            if obj_send_comments and obj.user.email:
              _send_mail(mail_title, tpl.render(c_author), mail_from, [obj.user.email])
          else:
            if parent.user == obj_user:
              if c.user == parent.user:
                pass
              else:
                if parent.send_comments and parent.email:
                    _send_mail(mail_title, tpl.render(c_user), mail_from, [parent.email])
            else:
              if obj_send_comments and obj.user.email:
                  _send_mail(mail_title, tpl.render(c_author), mail_from, [obj.user.email])
    
              if c.user and c.user == parent.user:
                pass
              else:
                if parent.send_comments and parent.email:
                    _send_mail(mail_title, tpl.render(c_user), mail_from, [parent.email])
      else:
        if not obj_user == c.user:
          if obj_send_comments and obj.user.email:
            _send_mail(mail_title, tpl.render(c_user), mail_from, [obj.user.email])
  except:
    pass

  return HttpResponseRedirect(obj.get_absolute_url())
  
def delete_comment(request,comment_id):
  try:
    c = get_object_or_404(Comment,pk=comment_id)
    obj = c.content_type.get_object_for_this_type(pk=int(c.object_id))
    if not request.user.is_anonymous() and (request.user.is_staff or request.user == obj.user or request.user == c.user):
      c.is_removed = 1
      c.save()
      
      # Якщо об'єкт вміє — встановити число коментарів
      try:
        obj.set_comments( None, Comment.objects.filter(content_type=c.content_type,object_id=obj.id,is_removed=False).count() )
      except:
        pass      
  except:
    pass
  return HttpResponseRedirect(obj.get_absolute_url())