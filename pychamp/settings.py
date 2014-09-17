"""
Django settings for pyChampion project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mm*m4rk3x9hsrm%c(-b1+xi8z4gahcm2+ueb7qap92w(9i%80y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

BROKER_URL = 'django://'

# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pyApp',
    'googlecharts',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
        'TIMEOUT': 900,
    }
}

ROOT_URLCONF = 'pychamp.urls'

WSGI_APPLICATION = 'pychamp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "static"),
        '/var/www/static/',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates')
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'pychamp.ct_processors.db_refresh_date',
    'pychamp.ct_processors.current_user_name',
    'pychamp.ct_processors.finding_track_dir',
    'pychamp.ct_processors.other_report_path'
)

# Settings For Testing
#FINDING_TRACK_DIR = "Z:/test_files_pychamp/Finding_Track"
#OTHER_REPORT_PATH = "Z:/test_files_pychamp/toolkit_data.xlsx"

# Custom Settings Uncomment for Production
FINDING_TRACK_DIR = "//phx-nas05-e3/groups06/ERAS/Map_Management/_finding_track_reports"
OTHER_REPORT_PATH = "//phx-nas05-e3/groups06/ERAS/Map_Management/_other_reports/toolkit_data.xlsx"

PICKLE_FILE = "user_settings.pkl"
REFRESH_KEY = 'DB_REFRESH_DATE'
