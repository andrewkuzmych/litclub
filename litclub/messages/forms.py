# coding=utf-8

from users.models import *
from messages.models import Topic
from messages.models import Message
from datetime import datetime

class SendMessageForm(forms.Manipulator):
    def __init__(self):
        self.fields = (
        forms.TextField(field_name="theme", length=75, max_length=50, is_required=True),
        forms.LargeTextField(field_name="body", max_length=1000, is_required=True),
        forms.HiddenField(field_name="userToId"),
        )

    def save(self, new_data, request, user_to = None):
        # current date
        datetime_now = datetime.now()

        # save topic
        topic = Topic()
        topic.theme = new_data['theme']
        topic.user1 = request.user

        if user_to is None:
            user_to = User.objects.get(id = new_data['userToId'])
        topic.user2 = user_to

        topic.create_on = datetime_now
        topic.update_on = datetime_now
        topic.save()

        # save message
        message = Message()
        message.user_from = topic.user1
        message.user_to = topic.user2
        message.topic = topic
        message.body = new_data['body']
        message.sent_on = datetime.now()
        message.save()

        return message


class ReplyMessageForm(forms.Manipulator):
    def __init__(self):
        self.fields = (
        forms.LargeTextField(field_name="body", max_length=1000, is_required=True),
        forms.HiddenField(field_name="topicId"),
        )

    def save(self, new_data, request):
        # current date
        datetime_now = datetime.now()

        # retrieve current topic
        topic = Topic.objects.get(id = new_data['topicId'])
        topic.update_on = datetime_now
        topic.save()

        # save message
        message = Message()
        message.user_from = request.user
        message.user_to = topic.get_companion(request.user)
        message.topic = topic
        message.body = new_data['body']
        message.sent_on = datetime_now
        message.save()

        return message

