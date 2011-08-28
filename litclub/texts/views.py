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
from texts.models import Text, Subscription, Read_text, Favorite
from texts.templatetags.texts import cattext

from django.conf import settings, LazySettings

def _send_mail(*kw):
    try:
        msg = EmailMessage(*kw)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    except:
        pass

def add_text(request, type):
    if request.user.is_authenticated():
        manipulator = Text.AddManipulator()

        try:
            r = int(request.GET.get('related', 0))
        except:
            r = 0

        if r:
            related = get_object_or_404(Text, id=request.GET.get('related', ''))
        else:
            related = None

        # check if user already submitted more than allowed
        count = Text.objects.filter(user=request.user,
                                    submit_date__gte=datetime.datetime.now().date(), type=type).count()

        if count >= LazySettings().PUBLICATION_LIMIT:
            return render_to_response('texts/limit_dialog.html',
                                      {'publication_limit': LazySettings().PUBLICATION_LIMIT},
                                      context_instance=RequestContext(request))

        if request.POST:
            new_data = request.POST.copy()
            new_data['type'] = type
            new_data['user'] = request.user.id
            new_data['comments_count'] = '0'
            new_data['rating'] = '0'
            new_data['rating_count'] = '0'
            errors = manipulator.get_validation_errors(new_data)

            if not errors:
                manipulator.do_html2python(new_data)

                # фільтр lictlub.us
                if re.search("litclub.{1,5}us", new_data['title'], re.I | re.M): return HttpResponseRedirect("/")
                if re.search("litclub.{1,5}us", new_data['text'], re.I | re.M): return HttpResponseRedirect("/")

                new_text = manipulator.save(new_data)
                request.user.get_profile().texts = -1
                request.user.get_profile().save()

                new_text.related = related
                new_text.save()

                if related:
                    tpl = loader.get_template('texts/mail_review.html')
                    context = Context({
                                          'text': related,
                                          'review': new_text,
                                          })
                    _send_mail(u"Рецензія на Літклубі", tpl.render(context), 'notify@litclub.org.ua',
                               [related.user.email])

                return HttpResponseRedirect("/texts/show/%i/" % new_text.id)
        else:
            errors = new_data = {}

        form = forms.FormWrapper(manipulator, new_data, errors)

        if type == '1' or type == '2' or type == '3':
           form.can_hide = 1

        return render_to_response('texts/add_form.html', {'form': form, 'type': type, 'related': related, },
                                  context_instance=RequestContext(request))

    else:
        return HttpResponseForbidden("403 Forbidden")

from django import newforms

class TextForm(newforms.Form):
    category = newforms.ChoiceField(label=u"Что это?", required=True, choices=(
    ("2", u"Поэзия"),
    ("1", u"Проза"),
    ("3", u"Другое"),
    ("5", u"Критика"),
    ("4", u"Тема на форум"),
    ))
    title = newforms.CharField(max_length=200, label=u"Название", help_text=u"",
                               widget=newforms.TextInput(attrs={'size': 70}, ), required=False)
    annotation = newforms.CharField(label=u"Аннотация", widget=newforms.Textarea(), required=False)
    text = newforms.CharField(label=u"Текст", widget=newforms.Textarea(), required=False)

def modify_text_publicator(request, mode, id=None):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    form = None

    if mode == 'add':

    # якщо автор зареєстрований менше місяця - може добавляти тільки 1 текст, інакше - 2.
        if datetime.datetime.now() - datetime.timedelta(days=30) > request.user.date_joined:
            n = 2
        else:
            n = 1
        ts = Text.objects.filter(user=request.user).order_by('-submit_date')[:n]
        if ts:
            s = 0
            for text in ts:
                if datetime.datetime.now().date() == text.submit_date.date():
                    s += 1
            if s == len(ts):
                return render_to_response('error_add_2_texts.html', {'message': n},
                                          context_instance=RequestContext(request))
                # by nelyud -------------------------------------------------------------------------

        text = Text()
    elif mode == 'change':
        text = get_object_or_404(Text, id=id)

    if request.method == 'POST':
        form = TextForm(request.POST)
        if form.is_valid():
            if mode == 'add':
                text.type = form.cleaned_data['category']
                text.user = request.user
                text.comments_count = 0
                text.rating = 0
                text.rating_count = 0
                text.title = form.cleaned_data['title']
                text.text = form.cleaned_data['text']
                text.annotation = form.cleaned_data['annotation']
                text.save()

                request.user.get_profile().texts = -1
                request.user.get_profile().save()
            elif mode == 'change':
                text.type = form.cleaned_data['category']
                text.title = form.cleaned_data['title']
                text.text = form.cleaned_data['text']
                text.annotation = form.cleaned_data['annotation']
                text.save()

            return HttpResponseRedirect("/texts/show/%i/" % text.id)
    if not form:
        if mode == 'add':
            form = TextForm()
        elif mode == 'change':
            fields = text.__dict__
            fields['category'] = text.type
            form = TextForm(fields)
    return render_to_response('texts/add_form_publicator.html', {'form': form, 'mode': mode},
                              context_instance=RequestContext(request))

def change_text(request, text_id):
    try:
        manipulator = Text.ChangeManipulator(text_id)
    except Text.DoesNotExist:
        return HttpResponseForbidden("403 Forbidden")

    text = manipulator.original_object

    if request.user.is_anonymous() or (not text.user == request.user and not request.user.is_staff):
        return HttpResponseForbidden("403 Forbidden")

    if request.POST:
        new_data = request.POST.copy()
        #new_data['type'] = unicode(text.type)
        new_data['user'] = unicode(text.user.id)
        new_data['rating'] = unicode(text.rating)
        new_data['rating_count'] = unicode(text.rating_count)
        new_data['comments_count'] = unicode(text.comments_count)
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            manipulator.save(new_data)
            return HttpResponseRedirect(text.get_absolute_url())
    else:
        errors = {}
        new_data = manipulator.flatten_data()

    form = forms.FormWrapper(manipulator, new_data, errors)
    categories = (( 2, u"Поезія"),
                  ( 1, u"Проза"),
                  ( 3, u"Інше"))
    if any(text.type == x for x,y in categories):
        form.category = text.type
        form.categories = categories
        
    return render_to_response('texts/change_form.html', {'form': form, 'text': text},
                              context_instance=RequestContext(request))

def delete_text(request, text_id):
    text = get_object_or_404(Text, pk=text_id)
    link = "/users/profile/%s/" % text.user.username

    if request.user.is_anonymous() or (not request.user.is_staff):
        return HttpResponseForbidden("403 Forbidden")

    text.user.get_profile().texts = -1
    text.user.get_profile().save()

    content_type = ContentType.objects.get(app_label='texts', model='text')
    for c in Comment.objects.filter(object_id=text.id, content_type=content_type):
        c.delete()

    text.delete()

    return HttpResponseRedirect(link)

def hide_text(request, text_id):
    text = get_object_or_404(Text, pk=text_id)
    link = "/texts/show/%s/" % text_id

    if request.user.is_anonymous() or (not text.user == request.user and not request.user.is_staff):
        return HttpResponseForbidden("403 Forbidden")

    text.is_hidden = 1
    text.save()

    return HttpResponseRedirect(link)

def open_text(request, text_id):
    text = get_object_or_404(Text, pk=text_id)
    link = "/texts/show/%s/" % text_id

    if request.user.is_anonymous() or (not text.user == request.user and not request.user.is_staff):
        return HttpResponseForbidden("403 Forbidden")

    text.is_hidden = 0
    text.save()

    return HttpResponseRedirect(link)

def list_texts(request, type=None):
    if type:
        obj = Text.objects.filter(type=type, is_hidden=0).order_by('-submit_date')
    else:
        obj = Text.objects.filter(type__in=[1, 2, 3, 5], is_hidden=0).order_by('-submit_date')
    paginator = ObjectPaginator(obj, 50)
    page = int(request.GET.get('page', '1'))
    try:
        texts = paginator.get_page(page - 1)
    except InvalidPage:
        texts = []

    # compose page title
    pageTitle = cattext(type)

    return render_to_response('texts/texts_list.html',
                              {'pagetitle': pageTitle, 'texts': texts, 'page': page,
                               'paginator': paginator, 'type': type},
                              context_instance=RequestContext(request))

def show_text(request, text_id):
    text = get_object_or_404(Text, id=text_id)
    if request.user.is_anonymous() or (not text.user == request.user and not request.user.is_staff):
    # only text owner can see own hidden texts
        if text.is_hidden == 1:
           return HttpResponseForbidden("403 Forbidden")
    else:
        text.can_change = 1


    if request.GET.get('rate', None):
        text.rate(request.user, request.GET.get('rate', None))

    client_address = request.META['REMOTE_ADDR']
    text.visit(client_address)
    text.visit_count = text.get_visit_count()

    text.can_rate = text._can_rate(request.user)

    # if current user is subscribed on this author then set text as read
    # check if current user is not anonymous
    if not request.user.is_anonymous():
        # check if user is subscribed on author of current text
        if Subscription.objects.filter(subscriber=request.user, publisher=text.user, is_active=True).count() > 0:
            # check if user already read current text
            if Read_text.objects.filter(text=text, read_by=request.user).count() == 0:
                # create record that current text was read by user
                read_text = Read_text(text=text, read_by=request.user)
                read_text.save()
        # ------------------------------------------------------------------

    # compose title
    user = User.objects.get(id=text.user.id)

    # use unicode(text.get_title(), 'UTF-8')
    try:
        pageTitle = text.get_title() + ", " + user.get_profile().name + " ( " + user.username + " )"
    except:
        pageTitle = text.get_title()
        pass

    if not request.user.is_anonymous() and text.type in [1, 2, 3, 5]:
        is_favorite_enabled = True
        is_favorite = Favorite.objects.filter(text=text, user=request.user).count() > 0
    else:
        is_favorite_enabled = False
        is_favorite = False

    return render_to_response('texts/text_detail.html',
                              {'pagetitle': pageTitle, 'u': request.user, 'text': text, 'type': str(text.type),
                               'is_favorite': is_favorite, 'is_favorite_enabled': is_favorite_enabled},
                              context_instance=RequestContext(request))

def main(request):
#texts = Text.objects.filter(type__in=[1,2,3]).order_by('-submit_date').extra( select = { 'one': " 1 /*" }, tables=['*/) AS `one` FROM `texts_text` force index (texts_text_submit_date) '])[:20]
    texts = Text.objects.filter(type__in=[1, 2, 3], is_hidden=0).order_by('-submit_date')[:20]
    reviews = Text.objects.filter(type=5).order_by('-submit_date')[:10]
    forum = Text.objects.filter(type=4).order_by('-submit_date')[:10]
    comments = Text.objects.all().order_by('-last_comment_date')[:20]

    odd = False
    for i in texts:
        i.odd = odd
        odd = not odd

    odd = False
    for i in forum:
        i.odd = odd
        odd = not odd

    odd = False
    for i in comments:
        i.odd = odd
        odd = not odd

    # рейтинги

    #.extra( select = { 'one': " 1 /*" }, tables=['*/) AS `one` FROM `texts_text` force index (texts_text_submit_date) '])
    #import datetime, time
    #month_ago = datetime.date.fromtimestamp(time.time() - 3600*24*30)
    #week_ago = datetime.date.fromtimestamp(time.time() - 3600*24*7)
    #top_month = Text.objects.filter(type__in=[1,2,3],rating_count__gt=2, submit_date__gt=month_ago).order_by('-rating','-rating_count')[:20]
    #top_all = Text.objects.filter(type__in=[1,2,3],rating_count__gt=4).order_by('-rating','-rating_count').extra( select = { 'one': " 1 /*" }, tables=['*/) AS `one` FROM `texts_text` force index (texts_text_rating) '])[:30]
    #top_week = Text.objects.filter(type__in=[1,2,3],rating_count__gt=1, submit_date__gt=week_ago).order_by('-rating','-rating_count')[:3]

    top = Text.objects.filter(type__in=[2, 3], rating__gt=0).order_by('-rating', '-submit_date', '-rating_count')[:20]
    week = Text.objects.filter(type__in=[1, 2, 3], rating__gt=0,
                               submit_date__gte=( datetime.date.today() - datetime.timedelta(days=7) )).order_by(
            '-rating', '-submit_date', '-rating_count')[:10]
    proza = Text.objects.filter(type__in=[1, ], rating__gt=0).order_by('-rating', '-submit_date', '-rating_count')[:20]
    return render_to_response('main.html',
                              {'texts': texts, 'forum': forum, 'reviews': reviews, 'comments': comments, 'top': top,
                               'week': week, 'proza': proza}, context_instance=RequestContext(request))


def rating_count(request):
    texts = Text.objects.all()
    for text in texts:
        text._rating_count()
        text.save()
    return HttpResponse('ok')


def comments_recount(request):
    from django.http import HttpResponse

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
    return HttpResponse('ok')

# --------------------------------------------------------------------------------------

# adds text to favorite. User can review favorite text on profile page
def add_to_favorite(request, text_id):
    if request.user.is_anonymous():
        return HttpResponseForbidden("403 Forbidden. Залогуйтеся спочатку !")

    # theme on forum can not be a favorite
    text = get_object_or_404(Text, id=text_id)
    if text.type not in [1, 2, 3, 5]:
        return render_to_response('error.html', {'error': 'Невірний тип твору'},
                                  context_instance=RequestContext(request))

    if Favorite.objects.filter(text=text, user=request.user).count() == 0:
        favorite = Favorite(text=text, user=request.user)
        favorite.save()

    return HttpResponseRedirect("/texts/show/" + str(text_id))

# removes text from favorite
def remove_from_favorite(request, text_id):
    if request.user.is_anonymous():
        return HttpResponseForbidden("403 Forbidden. Залогуйтеся спочатку !")

    text = get_object_or_404(Text, id=text_id)
    favorite = Favorite.objects.filter(text=text, user=request.user)
    favorite.delete()

    return HttpResponseRedirect("/texts/show/" + str(text_id))

# --------------------------------------------------------------------------------------