# coding=utf-8

from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    user1 = models.ForeignKey(User, related_name='user1')
    user2 = models.ForeignKey(User, related_name='user2')
    theme =  models.TextField(max_length=100)
    create_on = models.DateTimeField()
    update_on = models.DateTimeField()

    # returns all messages from the topic queue
    def get_messages(self):
        return Message.objects.filter(topic=self).order_by('sent_on')

    # returns the last message from the topic queue
    def get_last_message(self):
        #message = Message.objects.filter(topic=self).order_by('-sent_on')[0]
        message = Message.objects.filter(topic=self).latest('sent_on')
        return message

    # returns second participant in conversation
    def get_companion(self, current_user):
        if self.user1 == current_user:
            return self.user2
        else:
            return self.user1

     # returns count of messages which user didn't read
    def get_count_of_not_read_messages(self, current_user):
        return Message.objects.filter(topic=self, user_to=current_user, is_read=False).count()

    # set income messages as read
    def update_income_as_read(self, current_user):
        messages = Message.objects.filter(topic=self, user_to=current_user, is_read=False)
        for message in messages:
            message.is_read=True
            message.save()


class Message(models.Model):
    user_from = models.ForeignKey(User, related_name='user_from')
    user_to = models.ForeignKey(User, related_name='user_to')
    topic = models.ForeignKey(Topic)
    body =  models.TextField(max_length=1000)
    is_read = models.BooleanField(default=False)
    sent_on = models.DateTimeField()
    read_on = models.DateTimeField()
