# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime,timedelta
from random import random

from djlib.captcha.csettings import TIMEOUT
import sha

def future_datetime(**kw_args):
	def on_call():
		return datetime.now()+timedelta(**kw_args)
	return on_call
	
CAPTCHA_ANSWER_OK = 1 
CAPTCHA_UID_NOT_FOUND = -1
CAPTCHA_REQUEST_EXPIRED = -2
CAPTCHA_WRONG_ANSWER = -3

class Captcha(models.Model):
    text = models.CharField(max_length=10)
    sid = models.CharField(max_length=40,blank=True) # Session ID
    valid_until = models.DateTimeField(default=future_datetime(minutes=TIMEOUT),db_index=True)

    def save(self):
        shaobj = sha.new()
        # You can add anything you want here, if you're *really* serious
        # about an SID. This should be enough though
        shaobj.update(unicode(random()))
        shaobj.update(unicode(datetime.now()))
        shaobj.update(unicode(self.valid_until))
        shaobj.update(unicode(self.text))
        self.sid = shaobj.hexdigest()
        super(Captcha,self).save()

    @staticmethod
    def clean_expired():
        [x.delete() for x in Captcha.objects.filter(valid_until__lt=datetime.now())]

    @staticmethod
    def validate(sid,text):
        Captcha.clean_expired()
        result_list = Captcha.objects.filter(sid=sid)
        result = None
        if len(result_list)>0:
            result = result_list[0]
        if not result:
            return CAPTCHA_UID_NOT_FOUND
        if result.valid_until<datetime.now():
            result.delete()
            return CAPTCHA_REQUEST_EXPIRED 
        if result.text!=text:
            result.delete()
            return CAPTCHA_WRONG_ANSWER
        result.delete()
        return CAPTCHA_ANSWER_OK
    
    @staticmethod
    def new():
      captcha = Captcha()
      captcha.text = unicode(int(random()*10)) + unicode(int(random()*10)) + unicode(int(random()*10)) + unicode(int(random()*10)) + unicode(int(random()*10)) + unicode(int(random()*10))
      captcha.save()
      return captcha