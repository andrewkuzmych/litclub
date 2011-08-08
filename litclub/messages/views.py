# coding=utf-8
import thread
from django.contrib.auth.models import User
from django.core.paginator import ObjectPaginator

from forms import *

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from users.models import *
from django.db.models import Q

from django.core.mail import EmailMessage
from django.template import loader, Context

# sends email notification
def send_email_notification(message):
    # compose theme
    mail_theme = message.user_from.get_profile().get_name().encode('utf8') + \
                     u' надіслав Вам приватне повідомлення на ЛітКлубі.'.encode('utf8')

    # generate email body
    mail_template = loader.get_template('messages/income_notify.html')
    data_source = Context({'message': message})
    mail_body = mail_template.render(data_source)

    # send email
    msg = EmailMessage(mail_theme, mail_body, 'notify@litclub.org.ua', [message.user_to.email])
    msg.content_subtype = "html"
    msg.send()


# displays send message form
def send_form(request, userName):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    try:
        userTo = get_object_or_404(User, username=userName)
    except:
        raise Http404

    manipulator = SendMessageForm()
    new_data = {"userToId":userTo.id}
    form = forms.FormWrapper(manipulator, new_data)

    return render_to_response('messages/send.html',
                              {'form': form,
                               'userTo': userTo.get_profile(),
                               'userFrom': request.user.get_profile()},
                              context_instance=RequestContext(request))

# executes sending message procedure
def send_do(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    manipulator = SendMessageForm()
    new_data = request.POST.copy()
    errors = manipulator.get_validation_errors(new_data)

    if not errors:
        manipulator.do_html2python(new_data)
        # store message in data base
        message = manipulator.save(new_data, request)

        try:
            # send email notification about income message
            send_email_notification(message)
        except:
            pass

        return HttpResponseRedirect("/messages/topic/" + str(message.topic.id))

    else:
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('messages/send.html',
                              {'form': form,
                               'userTo': User.objects.get(id = new_data['userToId']).get_profile(),
                               'userFrom': request.user.get_profile()},
                              context_instance=RequestContext(request))

# displays all user's topics
def topics(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    # retrieve related topics
    user = request.user
    topics = Topic.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-update_on')

    paginator = ObjectPaginator(topics, 10)
    try:
        page = int(request.GET.get('page', '1'))
        topics = paginator.get_page(page - 1)
    except:
        page = 1
        topics = []

    # prepare data to display
    messages_command = []
    TopicDto = type('TopicDto', (object,), {})
    for topicItem in topics:
        topicDto = TopicDto()
        topicDto.topic = topicItem
        topicDto.companion = topicItem.get_companion(user)
        topicDto.not_read_messages_count = topicItem.get_count_of_not_read_messages(user)
        messages_command.append(topicDto)

    page_title = user.get_profile().get_name().encode('utf8') + ' : ' + u'Список приватних повідомлень '.encode('utf8')

    return render_to_response('messages/topics.html',
                              {'pagetitle': page_title,
                               'u': user.get_profile(), 'can_subscribe': False, 'can_unsubscribe': False,
                               'page':page, 'paginator':paginator,
                               'messages_command': messages_command,
                               'topics': topics},
                              context_instance=RequestContext(request))

# displays current topic and related messages
def topic(request, topicId):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    try:
        topic = get_object_or_404(Topic, id=topicId)
    except:
        raise Http404

    if topic.user1 != request.user and topic.user2 != request.user:
        return render_to_response('error.html',
                                  {'error':'Сторінка недоступна'},
                                  context_instance=RequestContext(request))

    # set as read income messages
    topic.update_income_as_read(request.user)

    messagesList = topic.get_messages()

    # prepare form
    manipulator = ReplyMessageForm()
    new_data = {'topicId':topicId}
    form = forms.FormWrapper(manipulator, new_data)

    page_title = topic.theme + ' ( ' + topic.user1.get_profile().get_name() + ' ' + topic.user2.get_profile().get_name() + ' ) '

    return render_to_response('messages/topic.html',
                              {'pagetitle':page_title,
                               'form': form,
                               'u': request.user.get_profile(), 'can_subscribe': False, 'can_unsubscribe': False,
                               'topic':topic,
                               'messagesList': messagesList},
                              context_instance=RequestContext(request))

# sends response to current topic
def reply(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    manipulator = ReplyMessageForm()
    new_data = request.POST.copy()
    errors = manipulator.get_validation_errors(new_data)

    # validate
    topicId = new_data["topicId"]
    try:
        topic = get_object_or_404(Topic, id=topicId)
    except:
        raise Http404

    if topic.user1 != request.user and topic.user2 != request.user:
        return render_to_response('error.html',
                                  {'error':'Сторінка недоступна'},
                                  context_instance=RequestContext(request))

    if not errors:
        manipulator.do_html2python(new_data)
        # store message in data base
        message = manipulator.save(new_data, request)

        try:
            # send email notification about income message
            send_email_notification(message)
        except:
            pass

        return HttpResponseRedirect("/messages/topic/" + str(topicId))
    else:
        messagesList = topic.get_messages()
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('messages/topic.html',
                              {'form': form,
                               'pagetitle':topic.theme,
                               'topic':topic,
                               'messagesList': messagesList},
                              context_instance=RequestContext(request))


# displays send message form
def send_spam_form(request):
    if not request.user.is_staff:
        return HttpResponseRedirect("/")

    manipulator = SendMessageForm()
    form = forms.FormWrapper(manipulator)

    return render_to_response('messages/send_spam.html',
                              {'form': form},
                              context_instance=RequestContext(request))

# executes sending message procedure
def send_spam_do(request):
    if not request.user.is_staff:
        return HttpResponseRedirect("/")

    manipulator = SendMessageForm()
    new_data = request.POST.copy()
    errors = manipulator.get_validation_errors(new_data)

    if not errors:
        manipulator.do_html2python(new_data)

        if request.POST.get('is_send_message', None) is not None:
            step = 100
            skip = 0
            take = step
            while True:
                users = list(User.objects.all().order_by("id")[skip:take])

                for user in users:
                    # store message in data base
                    manipulator.save(new_data, request, user)

                if User.objects.all()[skip:take + 1].count() == 0:
                    break
                else:
                    skip += step
                    take += step

        if request.POST.get('is_send_email', None) is not None:
            thread.start_new_thread(runSendEmailsProcess, (request.user, new_data))

        return HttpResponseRedirect("/")

    else:
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('messages/send_spam.html',
                              {'form': form},
                              context_instance=RequestContext(request))


# runs sending email process
def runSendEmailsProcess(user_from, new_data):
    step = 100
    skip = 0
    take = step
    while True:
        users = list(User.objects.all().order_by("id")[skip:take])

        for user in users:
            try:
                message = Message(user_from=user_from, user_to=user,
                                  body=new_data['body'], sent_on=datetime.now())
                # send email notification about income message
                send_email_notification(message)
            except:
                pass

        if User.objects.all()[skip:take + 1].count() == 0:
            break
        else:
            skip += step
            take += step