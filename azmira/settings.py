from pathlib import Path
from datetime import timedelta
import os

# GTK ইনস্টল করার পর যদি এই পাথে থাকে (সাধারণত এখানে থাকে)
GTK_PATH = r'C:\Program Files\GTK3-Runtime Win64\bin'
os.environ['PATH'] = GTK_PATH + os.pathsep + os.environ.get('PATH', '')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ol$9)r6^fs$k)^2al^^ru9i*(ufe)fxfre^izt8-ytlhx$90o9'

DEBUG = True
# AUTH_USER_MODEL = 'users.User'
AUTH_USER_MODEL = 'mainapp.ERPUser'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework_simplejwt",
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'mainapp.apps.MainappConfig',
    'users',
    'core',
    'accesscontrol',
    'django_celery_beat'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mainapp.middleware.ERPAutoLogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'azmira.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'azmira.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'azmira',             # ধাপ ১-এ Workbench-এ যে নাম দিয়েছেন
        'USER': 'root',                  # আপনার MySQL ইউজারনেম (ডিফল্ট root)
        'PASSWORD': 'Test1234*',     # আপনার MySQL Workbench-এর পাসওয়ার্ড
        'HOST': 'localhost',             # লোকালহোস্ট আইপি
        'PORT': '3306',                  # MySQL এর ডিফল্ট পোর্ট
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost:5173/,"
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # "DEFAULT_PERMISSION_CLASSES": (
    #     "rest_framework.permissions.IsAuthenticated",
    # ),
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}


SSL_WIRELESS_API_TOKEN = 'তোমার_api_token'   # SSL Wireless থেকে পাবে
SSL_WIRELESS_SENDER_ID = 'তোমার_sender_id'   # যেমন: AZMIRA

# Celery Configuration
CELERY_BROKER_URL     = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_TIMEZONE       = 'Asia/Dhaka'

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'auto-mark-absent-daily': {
        'task'    : 'mainapp.tasks.auto_mark_absent',
        'schedule': crontab(hour=23, minute=59),  # রাত ১১:৫৯
    },
    'generate-monthly-summary': {
        'task'    : 'mainapp.tasks.generate_monthly_summary',
        'schedule': crontab(hour=1, minute=0, day_of_month=1),  # মাসের ১ তারিখ
    },
    
     # প্রতিদিন সকাল ৯টায় 48h reminder
    'installment-reminder-48h': {
        'task':     'mainapp.tasks.send_installment_reminder_48h',
        'schedule': crontab(hour=9, minute=0),
    },
    # প্রতিদিন সকাল ১০টায় due today reminder  
    'installment-due-today': {
        'task':     'mainapp.tasks.send_installment_due_today',
        'schedule': crontab(hour=10, minute=0),
    },
}

