"""
Django settings for forge project.
Generated by 'django-admin startproject' using Django 2.2.6.
For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# To any curious GitHub readers: This isn't actually being used in prod. Don't worry.
SECRET_KEY = 'u$q*w!hvr(bvie*bo1c^!p!^cq%rsswx6jocx5yz2qw%1dc83$'

# SECURITY WARNING: don't run with debug turned on in production! Also, REMOVE * FROM ALLOWED_HOSTS!
DEBUG = True
ALLOWED_HOSTS = ["*"]


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
            'forge.context_processors.channels_url',
            'forge.context_processors.source_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'forge.wsgi.application'



# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'forge_octoprint',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'forgedevchannels.eastus.cloudapp.azure.com',
        'PORT': '1234',
    }
}

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
CHAT_SITE_URL="127.0.0.1"
CHAT_SITE_PORT=8001

# Allow pages to be loaded in a frame
X_FRAME_OPTIONS = 'ALLOW-FROM '+CHAT_SITE_URL



from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
INFLUX_URL="10.0.0.71"
INFLUX_PORT=80806
INFLUX_TOKEN = "txj6Z-GsYreT756jq01drVhmwRxNnlnzBri-cbFDFP9dgPZU7B0ItT5fhfJJAwebyI8TGAIkwIFlOLV36moLtw=="
influx_client = InfluxDBClient(url=INFLUX_URL+str(INFLUX_PORT), token=INFLUX_TOKEN)   
influx_write = influx_client.write_api(write_options=SYNCHRONOUS)
influx_query = influx_client.query_api()




#initialize google calendar
try:
    from forge.utils import google_calendar
    CALENDAR = google_calendar()
    print("SUCCESSFULLY STARTED CALENDAR")
except:
    CALENDAR = None
    print("FAILED TO START CALENDAR")
    
