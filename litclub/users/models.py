# coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core import validators
from litclub.texts.models import Text
from messages.models import Message
from texts.models import Subscription

class UserProfile(models.Model):
    userpic = models.ImageField(upload_to='userpics/', blank=True)
    username = models.CharField(max_length=30) # дублює поле з профілю
    email = models.CharField(max_length=60, blank=True, null=True) # дублює поле з профілю
    name = models.CharField(max_length=50, blank=True)
    about = models.TextField(blank=True)
    user = models.OneToOneField(User, primary_key=True)
    texts = models.IntegerField(default=0)
    rating = models.IntegerField(default=-1)
    green = models.BooleanField(default=False)
    comments = models.BooleanField(default=True)
    dont_show_ads = models.BooleanField(default=False)

    vkontakte = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=45, blank=True, null=True)
    country = models.CharField(max_length=45, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)

    # Антиспамовий показ пошти у профілі
    def split_email(self):
        return self.email.split('@')

    def get_all_texts(self):
        query = Text.objects.filter(user=self.user, type__in=[1, 2, 3, 5]);
        return query.order_by('type', '-submit_date')

    def get_texts(self):
        query = Text.objects.filter(user=self.user, type__in=[1, 2, 3, 5], is_hidden=0);
        return query.order_by('type', '-submit_date')

    def get_hidden_texts(self):
        query = Text.objects.filter(user=self.user, type__in=[1, 2, 3, 5], is_hidden=1);
        if self.current_user != self.user and not self.current_user.is_staff:
            return
        #if self.current_user != self.user:
        #    query = query.filter(is_hidden=0);
        return query.order_by('type', '-submit_date')

    def count_texts(self):
        query = Text.objects.filter(user=self.user, type__in=[1, 2, 3, 5], is_hidden=0);
        #if self.current_user != self.user:
        #    query = query.filter(is_hidden=0);
        return query.count()
        #if self.texts == -1:
        #    self.texts = query.count()
        #    self.save()
        #return self.texts
    def count_hidden_texts(self):
        query = Text.objects.filter(user=self.user, type__in=[1, 2, 3, 5], is_hidden=1);
        if self.current_user != self.user and not self.current_user.is_staff:
            return
        return query.count()

    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.user.username

    def get_url(self):
        return "/users/profile/%s" % self.user.username

    # returns count of income not read messages
    def get_count_of_all_not_read_messages(self):
        return Message.objects.filter(user_to=self.user, is_read=False).count()

    def get_count_of_not_read_subscription(self):
        subscriptions = Subscription.objects.filter(subscriber=self.user, is_active=True)
        count = Text.objects.filter(user__in=[subscription.publisher for subscription in subscriptions], type__in=[1, 2, 3, 4, 5]).extra(
                where=['id NOT IN (select text_id from texts_read_text where read_by_id = %s)'],
                params=[self.user.id]).count()
        return count

    # returns True if current user is publisher for input subscriber
    def is_publisher_for(self, subscriber):
        return Subscription.objects.filter(subscriber=subscriber, publisher=self.user, is_active=True).count() > 0

    # returns True if current user is subscriber for input publisher
    def is_subscriber_for(self, publisher):
        return Subscription.objects.filter(subscriber=self.user, publisher=publisher, is_active=True).count() > 0


class PasswordReset(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(max_length=32, db_index=True)
    date = models.DateTimeField(db_index=True, auto_now_add=True)

    @staticmethod
    def make_random_key(length=32, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        from random import choice

        return ''.join([choice(allowed_chars) for i in range(length)])


class ProfileChangeForm(forms.Manipulator):
    def __init__(self, user):

        COUNTRIES = (
            ("HIDDEN", "Не вказано"),
            ("UA", "Ukraine"),
            ("US", "United States"),
            ("RU", "Russia"),
            ("CA", "Canada"),
            ("DE", "Germany"),
            ("PL", "Poland"),
            ("RO", "Romania"),
            ("IT", "Italy"),
            ("MD", "Moldova"),
            ("ANOTHER", "Інша"),
        )

        GENDER = (
            ("HIDDEN", "Не вказано"),
            ("MALE", "Чоловіча"),
            ("FEMALE", "Жіноча"),
        )

        self.user = user
        self.fields = (
        forms.TextField(field_name="name", length=30, max_length=50, is_required=True),
        forms.LargeTextField(field_name="about", is_required=False),
        forms.EmailField(field_name="email", length=30, is_required=True),
        forms.TextField(field_name="vkontakte", length=30, max_length=100, is_required=False),
        forms.SelectField(field_name="gender", choices=GENDER),
        forms.SelectField(field_name="country", choices=COUNTRIES),
        forms.TextField(field_name="city", length=30, max_length=30, is_required=False),
        forms.CheckboxField(field_name="green"),
        forms.CheckboxField(field_name="comments"),
        forms.CheckboxField(field_name="dont_show_ads"),
        )

    def save(self, new_data):
        self.user.email = new_data['email']
        self.user.name = new_data['name']
        self.user.about = new_data['about']
        self.user.green = new_data['green']
        self.user.comments = new_data['comments']
        self.user.dont_show_ads = new_data['dont_show_ads']

        self.user.country = new_data['country']
        self.user.gender = new_data['gender']
        self.user.city = new_data['city']
        self.user.vkontakte = new_data['vkontakte']

        self.user.save()

        # update email in django user object
        self.user.user.email = new_data['email']
        self.user.user.save()

"""
class UserProfile(models.Model):
    userpic = models.ImageField(upload_to='userpics/',blank=True)
    username = models.CharField(max_length=30) # дублює поле з профілю
    email = models.CharField(max_length=60,blank=True, null=True) # дублює поле з профілю
    name = models.CharField(max_length=50,blank=True)
"""

# Ініціалізація djlib.users
import var

var.UserProfile = UserProfile
var.ProfileChangeForm = ProfileChangeForm
var.redirectAfterRegistration = '/users/change_profile/'