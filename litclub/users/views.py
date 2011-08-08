# coding=utf-8
from datetime import datetime

from django.contrib.auth.models import User

# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from texts.models import Subscription, Text, Read_text, Favorite

from var import *
from forms import *
from models import *

from django.contrib import auth
from django.conf import settings

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from users.models import *

import string, os
from PIL import Image

from django.conf import settings

#### moblog +
def _redirect(request, redirect=False):
    try:
        if not redirect:
            redirect = request.META['HTTP_REFERER']
        if string.find(redirect, request.META['PATH_INFO']) > -1:
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
    return render_to_response('users/login.html', {'redirect': redirect}, context_instance=RequestContext(request))

#### moblog +
def login_do(request):
    redirect = request.POST.get('redirect', '/')
    if redirect.find(loginURL) > -1 or redirect.find('reset_password_set') > -1 or redirect == '':
        redirect = '/'

    username = request.POST.get('username', None)
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    if not (username or email): return _redirect(request, loginURL)
    if email:
        try:
            username = User.objects.get(email=email).username
        except:
            pass
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        try:
            return _redirect(request, redirect)
        except:
            return _redirect(request, '/')
    else:
        return render_to_response('users/login.html',
                                  {'username': username, 'redirect': redirect, 'error': 'Невірний логін чи пароль'},
                                  context_instance=RequestContext(request))


    #### moblog +

def register(request):
    if not request.user.is_authenticated():
        manipulator = RegisterForm()
        if request.POST:
            new_data = request.POST.copy()
            errors = manipulator.get_validation_errors(new_data)
            if not errors:
                manipulator.do_html2python(new_data)
                manipulator.save(new_data, request)
                return HttpResponseRedirect(redirectAfterRegistration)
        else:
            errors = new_data = {}
        new_data['password1'] = new_data['password2'] = None
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('users/register.html', {'form': form, }, context_instance=RequestContext(request))

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
        return render_to_response('users/change_password.html', {'form': form, },
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")


def profile(request, username):
    try:
        user = get_object_or_404(User, username=username)
    except:
        raise Http404

    profile = user.get_profile()

    # compose page title
    pageTitle = profile.name + " ( " + profile.username + " )"

    return render_to_response('users/profile.html',
                              {'pagetitle': pageTitle, 'u': profile,
                               'can_subscribe': can_subscribe(request.user, user),
                               'can_unsubscribe': can_unsubscribe(request.user, user)},
                              context_instance=RequestContext(request))


def change_profile(request):
    if request.user.is_authenticated():
        profile = get_object_or_404(UserProfile, user=request.user)
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
        return render_to_response('users/change_profile.html', {'form': form, 'buser': profile},
                                  context_instance=RequestContext(request))
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
                if (not new_data['userpic'] or request.FILES.get('userpic_file', '')) and old_filename:
                    try:
                        os.remove(filename)
                    except:
                        pass
                    try:
                        os.remove(filename_s)
                    except:
                        pass
                if request.FILES.get('userpic_file', ''):
                    request.user.get_profile().save_userpic_file(
                            unicode(request.user.id) + "s",
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
                        im.save(filename, "JPEG", quality=90)

                    # ресайзим маленький аватар
                    im = Image.open(filename_s)
                    im = im.convert("RGB")
                    width, height = im.size
                    if width > 50 or height > 50:
                        im.thumbnail((50, 50), Image.ANTIALIAS)
                        im.save(filename_s, "JPEG", quality=90)
                request.user.message_set.create(message="Аватар змінено")
                return HttpResponseRedirect('/users/change_userpic/')
        else:
            errors = new_data = {}
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('users/change_userpic.html', {'form': form, 'user': request.user},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

def list(request):
    letters = u'абвгґдеєжзиіїйклмнопрстуфхцчшщьюяэёыъabcdefghijklmnopqrstuvwxyz#'
    i = 0
    order = {}
    for l in letters:
        order[l] = i
        i += 1

    #raise Exception( ''.join([k for k in letters]).encode('utf8') )

    users = UserProfile.objects.filter(texts__gte=3)
    for u in users:
        if not u.name: u.name = u.username
        #print u.name
        u.name = u.name.strip()
        try:
            u.first_letter = u.name[0]
        except:
            u.first_letter = '#'

        if not u.first_letter.lower() in (letters):
            u.first_letter = '#'
        u.first_letter = u.first_letter.upper()

    h = {}
    for u in users:
        if not h.get(u.first_letter, None):
            h[u.first_letter] = []
        h[u.first_letter].append(u)

    groups = []
    for fl in h:
        groups.append({'fl': fl, 'users': h[fl], 'column2': (fl.lower() in 'abcdefghijklmnopqrstuvwxyz#')})

    for g in groups:
        g['users'].sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))

    groups.sort(lambda a, b: cmp(order[a['fl'].lower()], order[b['fl'].lower()]))

    return render_to_response('users/list.html',
                              {'pagetitle':'Автори, які друкуються на Літклубі', 'groups': groups, 'page': 'authors'},
                              context_instance=RequestContext(request))

def reset_password(request):
    ok = False
    error = False
    key = ''
    if request.method == 'POST':
        if 'username' in request.POST:
            try:
                user = User.objects.get(username=request.POST['username'])
            except:
                user = None

            if user:
                if user.get_profile().email or user.email:
                    pr = PasswordReset(user=user, key=PasswordReset.make_random_key())
                    pr.save()
                    key = pr.key

                    from django.template import Context, loader
                    from django.core.mail import send_mail

                    t = loader.get_template("users/email_password_reset.txt")
                    c = {'pr': pr}

                    if settings.LANGUAGE_CODE == 'uk':
                        subject = u'Відновлення паролю на Літклубі'
                    else:
                        subject = u'Восстановление пароля на Публикаторе'

                    send_mail(subject, t.render(Context(c)), None, [user.get_profile().email or user.email])

                    ok = True
                else:
                    error = 'email'
            else:
                error = 'user'

    return render_to_response('users/reset_password.html',
                              {'ok': ok, 'error': error, 'username': request.POST.get('username', ''), 'key': key},
                              context_instance=RequestContext(request))

def reset_password_set(request):
    ok = False
    error = ''

    try:
        import datetime

        pr = PasswordReset.objects.get(key=request.GET.get('key', ''),
                                       date__gte=datetime.datetime.today() - datetime.timedelta(days=3))
        PasswordReset.objects.filter(date__lt=datetime.datetime.today() - datetime.timedelta(days=4)).delete()
    except:
        pr = None

    if pr:
        if request.method == 'POST':
            if 'password1' in request.POST and 'password2' in request.POST:
                if not request.POST['password1']:
                    error = 'none'
                elif request.POST['password1'] != request.POST['password2']:
                    error = 'diff'
                else:
                # Встановити пароль
                    pr.user.set_password(request.POST['password1'])
                    pr.user.save()
                    pr.delete()
                    ok = True

    return render_to_response('users/reset_password_set.html', {'pr': pr, 'pr': pr, 'error': error, 'ok': ok},
                              context_instance=RequestContext(request))

# --------------------------------------------------------------------------------------

# executes subscribing current user on selected publisher
# NOTE all texts will be marked as read
def subscribe(request, publisher_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")
    
    try:
        publisher = get_object_or_404(User, id=publisher_id)
    except:
        raise Http404

    if Subscription.objects.filter(subscriber=request.user, publisher=publisher).count() > 0:
        subscription = Subscription.objects.filter(subscriber=request.user, publisher=publisher).latest('create_on')
        if subscription.is_active:
            print "You are already subscribed"
        else:
            subscription.is_active = True
            subscription.update_on = datetime.now()
            subscription.save()
            # mark new texts as read
            texts = get_not_read_texts(subscription.publisher, request.user)
            for text in texts:
                read_text = Read_text(text=text, read_by=request.user)
                read_text.save()
    else:
        subscription = Subscription(publisher=publisher, subscriber=request.user)
        subscription.save()
        # mark all texts as read
        texts = Text.objects.filter(user=subscription.publisher, type__in=[1, 2, 3, 4, 5])
        for text in texts:
            read_text = Read_text(text=text, read_by=request.user)
            read_text.save()

    return HttpResponseRedirect("/users/subscription/")

# executes unsubscribing of current user from selected publisher
def unsubscribe(request, publisher_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    try:
        publisher = get_object_or_404(User, id=publisher_id)
    except:
        raise Http404

    if Subscription.objects.filter(subscriber=request.user, publisher=publisher, is_active=True).count() > 0:
        subscription = Subscription.objects.filter(subscriber=request.user, publisher=publisher, is_active=True).latest('create_on')
        subscription.is_active = False
        subscription.update_on = datetime.now()
        subscription.save()
    else:
        print "You are not subscribed"

    return HttpResponseRedirect("/users/subscription/")

# displays subscriptions of current logged user
def subscription_own(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    current_user = request.user
    subscriptions = Subscription.objects.filter(subscriber=current_user, is_active=True)
    subscriptions = sorted(subscriptions, key=sort_by_user_name)

    # prepare data to display
    command = []
    SubscriptionDto = type('SubscriptionDto', (object,), {})
    for subscription in subscriptions:
        subscriptionDto = SubscriptionDto()
        subscriptionDto.publisher = subscription.publisher
        subscriptionDto.new_texts = get_not_read_texts(subscription.publisher, current_user)
        command.append(subscriptionDto)

    page_title = current_user.get_profile().get_name().encode('utf8') + ' : ' + u'Підписка'.encode('utf8')

    return render_to_response('users/subscription.html',
                              {'pagetitle': page_title,
                               'u': current_user.get_profile(),
                               'can_subscribe': False,
                               'can_unsubscribe': False,
                               'subscription_command':command},
                              context_instance=RequestContext(request))

# displays subscriptions of selected user
def subscription_of(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
    except:
        raise Http404

    page_title = user.get_profile().get_name().encode('utf8') + ' : ' + u'Підписка'.encode('utf8')

    subscriptions = Subscription.objects.filter(subscriber=user, is_active=True)
    subscriptions = sorted(subscriptions, key=sort_by_user_name)

    return render_to_response('users/subscription_of.html',
                              {'pagetitle': page_title,
                               'u': user.get_profile(),
                               'can_subscribe': can_subscribe(request.user, user),
                               'can_unsubscribe': can_unsubscribe(request.user, user),
                               'subscriptions': subscriptions},
                              context_instance=RequestContext(request))

# sorts by publisher name
def sort_by_user_name(subscription):
    return str.lower(subscription.publisher.get_profile().get_name().encode('utf8'))

# returns True if subscriber can subscribe on publisher
# if subscriber is anonymous returns False
def can_subscribe(subscriber, publisher):
    if subscriber.is_anonymous() or subscriber == publisher :
        return False

    if publisher.get_profile().is_publisher_for(subscriber):
        return False
    else:
        return True

# returns True if subscriber can unsubscribe on publisher
# if subscriber is anonymous returns False
def can_unsubscribe(subscriber, publisher):
    if subscriber.is_anonymous() or subscriber == publisher :
        return False

    if subscriber.get_profile().is_subscriber_for(publisher):
        return True
    else:
        return False

# returns texts witch ware not read by subscriber and posted by publisher
def get_not_read_texts(publisher, subscriber):
    return Text.objects.filter(user=publisher, type__in=[1, 2, 3, 4, 5]).extra(
                where=['id NOT IN (select text_id from texts_read_text where read_by_id = %s)'],
                params=[subscriber.id])

# --------------------------------------------------------------------------------------

# Favorite engine.

# Displays favorite texts of current active user
def favorite_texts_own(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect("/")

    return favorite_texts(request, request.user.id)

# Displays favorite texts of selected user
def favorite_texts(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
    except:
        raise Http404

    texts = [v.text for v in Favorite.objects.filter(user=user).order_by('-create_on')]

    page_title = user.get_profile().get_name().encode('utf8') + ' : ' + u'Улюблені твори'.encode('utf8')

    return render_to_response('users/favorite_texts.html',
                              {'pagetitle': page_title,
                               'u': user.get_profile(),
                               'can_subscribe': can_subscribe(request.user, user),
                               'can_unsubscribe': can_unsubscribe(request.user, user),
                               'texts': texts},
                              context_instance=RequestContext(request))

# --------------------------------------------------------------------------------------


