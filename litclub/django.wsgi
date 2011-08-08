import os
import sys

sys.path.append('D:\Development\litclub\litclub\litclub\litclub\django')
sys.path.append('D:\Development\litclub\litclub\litclub\litclub')
print >> sys.stderr, sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'litclub.settings_litclub'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
