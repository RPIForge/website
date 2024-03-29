"""
Django settings for forge project.
Generated by 'django-admin startproject' using Django 2.2.6.
For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from decouple import config
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# To any curious GitHub readers: This isn't actually being used in prod. Don't worry.
SECRET_KEY = config('SECRET_KEY',default=get_random_secret_key(), cast=str)

# SECURITY WARNING: don't run with debug turned on in production! Also, REMOVE * FROM ALLOWED_HOSTS!
DEBUG = config('DEBUG',default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS',default='*', cast=lambda v: [s.strip() for s in v.split(',')])


# Application definition
INSTALLED_APPS = [
    'forge.apps.MachineUsageConfig',
    'forge.apps.MachineManagementConfig',
    'forge.apps.MyForgeConfig',
    'forge.apps.UserManagementConfig',
    'forge.apps.ForgeConfig',
    'forge.apps.APIConfig',
    'forge.apps.BusinessConfig',
    'forge.apps.DataManagementConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'forge.urls'

TEMPLATES = [
    {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'forge.context_processors.channels_url'
            ],
        },
    },
]

WSGI_APPLICATION = 'forge.wsgi.application'



# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_DB',default="ruwebsite_db"),
        'USER': config('POSTGRES_USER',default="postgres"),
        'PASSWORD': config('POSTGRES_PASSWORD',default="password"),
        'HOST': config('POSTGRES_HOST',default="db"),
        'PORT': config('POSTGRES_PORT',default="5432"), 
    }
}

## Set default Primary Keys
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Login

LOGIN_URL = '/login'

# Chat settings
CHAT_SITE_URL=config('CHAT_SITE_URL',default="127.0.0.1")
CHAT_SITE_PORT=config('CHAT_SITE_PORT',default="8001",cast=int)
CHAT_SITE_HTTPS = config('CHAT_SITE_HTTPS',default=True,cast=bool)
FAILURE_FORM_URL=config('FAILURE_FORM_URL',default='https://t0tfudyw7g.execute-api.us-east-1.amazonaws.com/main')

if(CHAT_SITE_HTTPS):
    CHAT_SITE = "https://{}:{}".format(CHAT_SITE_URL,CHAT_SITE_PORT)
else:
    CHAT_SITE = "http://{}:{}".format(CHAT_SITE_URL,CHAT_SITE_PORT)

# Allow pages to be loaded in a frame
X_FRAME_OPTIONS = 'ALLOW-FROM '+CHAT_SITE_URL


#initialize google calendar
try:
    from forge.utils import google_calendar
    CALENDAR = google_calendar()
    print("SUCCESSFULLY STARTED CALENDAR")
except:
    CALENDAR = None
    print("FAILED TO START CALENDAR")
    
