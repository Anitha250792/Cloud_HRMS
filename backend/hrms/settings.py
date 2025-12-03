# hrms/settings.py
import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "your-secret-key"

DEBUG = False

ALLOWED_HOSTS = ["*",".railway.app"]

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_crontab",

    # 3rd party apps
    "rest_framework",
    "corsheaders",
    

    # Local apps
    "employees",
    "attendance",
    "payroll",
    "leave",

]

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Root URL Configuration (MISSING earlier — now added)
ROOT_URLCONF = "hrms.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI (required)
WSGI_APPLICATION = "hrms.wsgi.application"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ]
}

CRONJOBS = [
    ('0 0 1 * *', 'payroll.cron.generate_monthly_payroll'),
]


# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Database (PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hrms_db",
        "USER": "postgres",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Static files
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BEAT_SCHEDULE = {
    "generate-monthly-payroll-on-1st": {
        "task": "payroll.tasks.generate_monthly_payroll",
        "schedule": crontab(day_of_month=1, hour=1, minute=0),  # 1st of every month at 01:00
        "args": (),  # year/month auto-picked in task
    },
}

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Windows fix — use solo worker instead of prefork
CELERYD_FORCE_EXECV = True
CELERY_WORKER_POOL = "solo"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "ntanithasaravanan@gmail.com"
EMAIL_HOST_PASSWORD = "ebxj uouc mhcm pycr"
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

