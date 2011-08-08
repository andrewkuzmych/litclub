# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from djlib.users.var import *
from djlib.users.forms import *

from django.contrib import auth
from django.conf import settings

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

import string, os
from PIL import Image

#### moblog +
def _redirect(request,redirect=False):
  try:
    if not redirect:
      redirect = request.META['HTTP_REFERER']
    if string.find(redirect,request.META['PATH_INFO']) > -1:
      redirect = '/'
  except:
    redirect = '/'
  return HttpResponseRedirect(redirect)
    
#### moblog +
def logout_do(request):
  auth.logout(request)
  return _redirect(request)

#### moblog +
def login(request):
  try:
    redirect = request.META['HTTP_REFERER']
  except:
    redirect = ''
  return render_to_response('users/login.html', { 'redirect': redirect }, context_instance=RequestContext(request))

#### moblog +
def login_do(request):
  try:
    redirect = request.POST['redirect']
  except:
    redirect = '/'
  try:
    if (redirect.index(loginURL)):
      redirect = '/'    
  except:
    pass
  if redirect == '':
    redirect = '/'
  
  username = request.POST.get('username',None)
  email = request.POST.get('email','')
  password = request.POST.get('password','')
  if not (username or email): return _redirect(request,loginURL)
  if email:
    try:
      username = User.objects.get(email=email).username
    except:
      pass
  user = auth.authenticate(username=username, password=password)
  if user is not None:
      auth.login(request, user)
      try:
        return _redirect(request,redirect)
      except:
        return _redirect(request,'/')
  else:
      return render_to_response('users/login.html', { 'username': username, 'redirect': redirect, 'error': 'Невірний логін чи пароль' }, context_instance=RequestContext(request))
    

#### moblog +
def register(request):
  if not request.user.is_authenticated():
    manipulator = RegisterForm()
    if request.POST:
      new_data = request.POST.copy()
      errors = manipulator.get_validation_errors(new_data)
      if not errors:
        manipulator.do_html2python(new_data)
        manipulator.save(new_data,request)
        return HttpResponseRedirect(redirectAfterRegistration)
    else:
      errors = new_data = {}
    new_data['password1'] = new_data['password2'] = None
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response('users/register.html',{'form': form, }, context_instance=RequestContext(request))
    
  else:
    return HttpResponseRedirect("/")
    
    
#### moblog +
def register_ok(request):
  return render_to_response('users/register_ok.html', {}, context_instance=RequestContext(request))

#### moblog +
def change_password(request):
  if request.user.is_authenticated():
    manipulator = PasswordChangeForm(request.user)
    if request.POST:
      new_data = request.POST.copy()
      errors = manipulator.get_validation_errors(new_data)
      if not errors:
        manipulator.do_html2python(new_data)
        manipulator.save(new_data)
        request.user.message_set.create(message="Пароль змінено")
        return HttpResponseRedirect('/users/change_password/')
    else:
      errors = {}
      new_data = {}
    new_data = {} # Щоб паролі не передавалися у форму
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response('users/change_password.html',{'form': form, }, context_instance=RequestContext(request))
  else:
    return HttpResponseRedirect("/")
    
    
  
def profile(request,username):
  user = get_object_or_404(User,username=username)
  user = user.get_profile()
  return render_to_response('users/profile.html', { 'u': user }, context_instance=RequestContext(request))
  

def change_profile(request):
  if request.user.is_authenticated():
    profile = get_object_or_404(UserProfile,user=request.user)
    manipulator = ProfileChangeForm(profile)
    if request.POST:
      new_data = request.POST.copy()
      errors = manipulator.get_validation_errors(new_data)
      if not errors:
        manipulator.do_html2python(new_data)
        manipulator.save(new_data)
        request.user.message_set.create(message="Дані змінено")
        return HttpResponseRedirect('/users/change_profile/')
    else:
      errors = {}
      new_data = {}
      
      # Додає в new_data всі дані з profile. В моделі UserProfile поля можуть бути будь-які
      # Тут використовується недокументована змінна _meta, варто буде це змінити
      for field in profile._meta.fields:
        new_data[field.name] = eval("profile.%s" % field.name)

    form = forms.FormWrapper(manipulator, new_data, errors)
    profile.now_user = 1
    return render_to_response('users/change_profile.html',{'form': form, 'buser': profile }, context_instance=RequestContext(request))
  else:
    return HttpResponseRedirect("/")
      
def change_userpic(request):
  if request.user.is_authenticated():
    manipulator = UserpicChangeForm(request.user) 
    if request.FILES:
      new_data = request.POST.copy()
      new_data.update(request.FILES)
      errors = manipulator.get_validation_errors(new_data)
      if not errors:
        filename = settings.MEDIA_ROOT + "userpics/" + unicode(request.user.id)
        filename_s = filename + "s"
        manipulator.do_html2python(new_data)
        old_filename = manipulator.original_object.userpic and manipulator.original_object.get_userpic_filename()
        profile = manipulator.save(new_data)
        if (not new_data['userpic'] or request.FILES.get('userpic_file','')) and old_filename:
          try:
            os.remove(filename)
          except:
            pass
          try:
            os.remove(filename_s)
          except:
            pass
        if request.FILES.get('userpic_file',''):
          request.user.get_profile().save_userpic_file(
            unicode(request.user.id)+"s",
            request.FILES['userpic_file']['content'])            
          request.user.get_profile().save_userpic_file(
            unicode(request.user.id),
            request.FILES['userpic_file']['content'])                     
          
          # ресайзим великий аватар
          im = Image.open(filename)
          width, height = im.size
          if width > 100 or height > 100:
            im = im.convert("RGB")
            im.thumbnail((100, 100), Image.ANTIALIAS)
            im.save(filename, "JPEG", quality = 90)        
          
          # ресайзим маленький аватар
          im = Image.open(filename_s)
          im = im.convert("RGB")
          width, height = im.size
          if width > 50 or height > 50:
            im.thumbnail((50,50), Image.ANTIALIAS)
            im.save(filename_s, "JPEG", quality = 90)        
        request.user.message_set.create(message="Аватар змінено")
        return HttpResponseRedirect('/users/change_userpic/')
    else:
      errors = new_data = {}
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response('users/change_userpic.html',{'form': form, 'user': request.user}, context_instance=RequestContext(request))
  else:
    return HttpResponseRedirect("/")
