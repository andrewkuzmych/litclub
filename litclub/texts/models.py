# coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class Text(models.Model):
    user = models.ForeignKey(User)
    # proza - 1
    # poezija - 2
    # inshe - 3
    # forum - 4
    # retsenzija - 5
    type = models.SmallIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    annotation = models.TextField(blank=True, null=True)
    submit_date = models.DateTimeField(auto_now_add=True, db_index=True)
    comments_count = models.IntegerField()
    allow_comments = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    rating = models.IntegerField(db_index=True, blank=True, null=True)
    rating_count = models.IntegerField()
    last_comment_date = models.DateTimeField(blank=True, null=True, db_index=True)
    last_comment_user = models.ForeignKey(User, blank=True, null=True, related_name="last_comment_user")

    related = models.ForeignKey('self', blank=True, null=True, related_name='related_text')

    ret = []

    def get_title(self):
        if self.title:
            return self.title
        else:
            return "(без назви)"

    def get_is_hidden(self):
        return self.is_hidden

    def get_absolute_url(self):
        return "/texts/show/%s/" % self.id

    def get_rating(self):
        return self.rating

    def set_comments(self, last_comment, count):
        self.comments_count = count
        if last_comment:
            self.last_comment_date = last_comment.submit_date
            self.last_comment_user = last_comment.user
        self.save()

    # Додає голос за текст (новий Vote)
    def rate(self, user, value):
        rating = 0
        if value == "plus":
            rating = 1
        elif value == "minus":
            rating = -1

        # Якщо користувач авторизований та ще не голосував
        if not (user.is_anonymous() or Vote.objects.filter(text=self, user=user)[:1]):
        # Якщо є голос
        #raise Exception(rating)
            if rating:
                Vote(user=user, text=self, value=rating).save()

        self._rating_count()
        self.save()

    # Додати цей перегляд до списку переглядів
    def visit(self, ipaddress):
        existIp = 0
        for v in Visit.objects.filter(text=self):
            if (ipaddress == v.ipaddress):
                existIp = 1
                break
        if not existIp:
            Visit(text=self, ipaddress=ipaddress).save()

        self.save()

    # Чи може користувач рейтингувати цей текст
    def _can_rate(self, user):
    # З підкресленням, бо через необхідність у інформації про користувача цей метод не можна викликати напряму з шаблону.
    # Тому він викликається з функції показу тексту як text.can_rate = text._can_rate(user)
    # Якщо user автор тексту або його голос вже є, то голосувати не можна
        if user.is_anonymous() or user == self.user or Vote.objects.filter(text=self, user=user)[:1]:
            return 0
        return 1


    # Розраховує рейтинг тексту
    def _rating_count(self):
        rating = 0
        rating_count = 0

        for v in Vote.objects.filter(text=self):
            rating += v.value
            rating_count += 1

        self.rating = rating
        self.rating_count = rating_count

    # Розраховує кількість переглядів тексту
    def get_visit_count(self):
        visit_count = Visit.objects.filter(text=self).count()
        return visit_count

# Голоси людей. За ними можна розрахувати рейтинг; сам рейтинг зберігається у тексті
class Vote(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, related_name='rel_vote_user')
    text = models.ForeignKey(Text)
    value = models.IntegerField()

class Visit(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    text = models.ForeignKey(Text)
    ipaddress = models.CharField(max_length=255)

# models for subscription engine
class Subscription(models.Model):
    publisher = models.ForeignKey(User, related_name='text_publisher')
    subscriber = models.ForeignKey(User, related_name='text_subscriber')
    create_on = models.DateTimeField(auto_now_add=True, db_index=True)
    update_on = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class Read_text(models.Model):
    text = models.ForeignKey(Text)
    read_by = models.ForeignKey(User)
    read_on = models.DateTimeField(auto_now_add=True, db_index=True)
    
# end of models for subscription engine
# -----------------------------------------------

class Favorite(models.Model):
    text = models.ForeignKey(Text)
    user = models.ForeignKey(User)
    create_on = models.DateTimeField(auto_now_add=True, db_index=True)