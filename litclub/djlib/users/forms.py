# -*- coding: utf-8 -*-

from django import forms
from django.core import validators
from django.contrib.auth.models import User 
from djlib.users.var import *
from django.contrib import auth

class RegisterForm(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=30, max_length=30, is_required=True, validator_list=[validators.isAlphaNumeric, validators.isLowerCase, self.isValidUsername]),
            forms.EmailField(field_name="email", length=30, is_required=True),       
            forms.PasswordField(field_name="password1", length=30, max_length=30, is_required=True,
                validator_list=[validators.AlwaysMatchesOtherField('password2', "Паролі не співпадають")]),
            forms.PasswordField(field_name="password2", length=30, max_length=30, is_required=True),
        )

    def isValidUsername(self, new_data, all_data):
      if User.objects.filter(username=new_data):
          raise validators.ValidationError, "Користувач з таким логіном вже є. Виберіть інший логін."

    def save(self, new_data, request):
        user = User.objects.create_user(new_data['username'], new_data['email'], new_data['password1'])
        user.save()
        userprofile = UserProfile(user=user)
        userprofile.texts = 0
        userprofile.username = new_data['username']
        userprofile.email = new_data['email']
        userprofile.save()
        user = auth.authenticate(username=new_data['username'], password=new_data['password1'])
        if user is not None:    
          auth.login(request, user)


class PasswordChangeForm(forms.Manipulator):
    def __init__(self, user):
        self.user = user
        self.fields = (
            forms.PasswordField(field_name="old_password", length=30, max_length=30, is_required=True,
                validator_list=[self.isValidOldPassword]),
            forms.PasswordField(field_name="new_password1", length=30, max_length=30, is_required=True,
                validator_list=[validators.AlwaysMatchesOtherField('new_password2', "Паролі не співпадають")]),
            forms.PasswordField(field_name="new_password2", length=30, max_length=30, is_required=True),
        )

    def isValidOldPassword(self, new_data, all_data):
        if not self.user.check_password(new_data):
            raise validators.ValidationError, "Пароль невірний."

    def save(self, new_data):
        self.user.set_password(new_data['new_password1'])
        self.user.save()
        
        
class UserpicChangeForm(forms.Manipulator):
    def __init__(self, user):
        self.user = user
        self.original_object = user.get_profile()
        self.fields = (
            forms.FileUploadField(field_name="userpic_file"),
            forms.HiddenField(field_name="userpic"),
        )

    def save(self, new_data):
        profile = self.user.get_profile()
        profile.userpic = new_data['userpic']
        profile.save()