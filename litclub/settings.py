# Django settings for litclub project.
import sys
sys.path.append('/home/django')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Nvc', 'nvc@nvc.com.ua'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'litclub'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'root'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '3306'             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'EET'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'uk'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'D:/project/litclub/src/media/litclub/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = 'http://localhost:8080/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4l@(m1!f6q&*_@k)rpbftuh3)r(pd1mt5x8=^ds+5ju)nj$kml'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
#    'litclub.lib.TimeLogMiddleware'
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

)

ROOT_URLCONF = 'litclub.urls.lc'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/nelyud/litclub/litclub/templates/litclub', '/home/nelyud/litclub/litclub/templates',
    'D:/project/litclub/src/litclub/templates',
    'D:/project/litclub/src/litclub/templates/litclub',
    '/home/litclub/litclub/www/litclub/litclub/templates/litclub','/home/litclub/litclub/www/litclub/litclub/templates',
    '/home/litclub/litclub/www/litclub/templates/litclub','/home/litclub/litclub/www/litclub/litclub/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'litclub.users',
    'litclub.texts',
    'litclub.messages',
    'djlib.comments',
    'djlib.captcha',
)

AUTH_PROFILE_MODULE = 'users.UserProfile'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'litclubua@gmail.com'
EMAIL_HOST_PASSWORD = 'scromnist'
EMAIL_USE_TLS = True

# how many publications per day can author do
PUBLICATION_LIMIT = 3