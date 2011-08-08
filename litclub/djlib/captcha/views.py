# -*- coding: utf-8 -*-
from django.http import HttpResponse
from djlib.captcha.models import Captcha
from cStringIO import StringIO
import random
from django.shortcuts import get_object_or_404

from djlib.captcha.csettings import FONT_PATH
import os
import Image
import cStringIO # *much* faster than StringIO
import urllib
import settings
import ImageFilter
import ImageFont, ImageDraw

def captcha_image(request,sid):
    captcha = get_object_or_404(Captcha,sid=sid)
    text = captcha.text
   
    image = gen_captcha(text, os.path.join(settings.MEDIA_ROOT,'Captcha/captcha.ttf'), 25, "captcha.jpg")

    image_data = open("captcha.jpg", "rb").read()
    return HttpResponse(image_data, mimetype="image/JPEG")

def gen_captcha(text, fnt, fnt_sz, file_name, fmt='GIF'):
	"""Generate a captcha image"""
	# randomly select the foreground color
	fgcolor = 0xffff00
	# make the background color the opposite of fgcolor
	bgcolor = fgcolor ^ 0xffffff
	# create a font object
	font = ImageFont.truetype(fnt,fnt_sz)
	# determine dimensions of the text
	dim = font.getsize(text)
	# create a new image slightly larger that the text
	im = Image.new('RGB', (dim[0]+5,dim[1]+5), bgcolor)
	d = ImageDraw.Draw(im)
	x, y = im.size
	r = random.randint
	# draw 100 random colored boxes on the background
	for num in range(100):
		d.rectangle((r(0,x),r(0,y),r(0,x),r(0,y)),fill=r(0,0xffffff))
	# add the text to the image
	d.text((3,3), text, font=font, fill=fgcolor)

	im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
	# save the image to a file
	im.save(file_name, format=fmt)


