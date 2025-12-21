import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================
# 🔐 CORE SETTINGS
# ======================================================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "cloud-hrms-1.onrender.com",
    "cloud-hrms-frontend-1.onrender.com",
    "localhost",
    "127.0.0.1",
]

SITE_ID = 1

# ======================================================
# 📦 INSTALLED APPS
# ======================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_crontab",

    # Auth (EMAIL / PASSWORD ONLY)
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",

    # Local apps
    "employees",
    "attendance",
    "payroll",
    "leave",
    "accounts",
]

# ======================================================
# 🔑 REST + JWT
# ======================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ======================================================
# 🧱 MIDDLEWARE
# ======================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "allauth.account.middleware.AccountMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ======================================================
# 🌐 URL / TEMPLATES
# ======================================================

ROOT_URLCONF = "hrms.urls"

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

WSGI_APPLICATION = "hrms.wsgi.application"

# ======================================================
# 🔐 AUTH CONFIG (EMAIL LOGIN ONLY)
# ======================================================

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ======================================================
# 🗄 DATABASE (RENDER SAFE)
# ======================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=False,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ======================================================
# 📁 STATIC FILES
# ======================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================================================
# 🌍 CORS + CSRF
# ======================================================

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    "https://cloud-hrms-1.onrender.com",
    "https://cloud-hrms-frontend-1.onrender.com",
]

CSRF_USE_SESSIONS = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ======================================================
# ⏱ CRON + CELERY
# ======================================================

CRONJOBS = [
    ("0 0 1 * *", "payroll.cron.generate_monthly_payroll"),
]

CELERY_BEAT_SCHEDULE = {
    "generate-monthly-payroll-on-1st": {
        "task": "payroll.tasks.generate_monthly_payroll",
        "schedule": crontab(day_of_month=1, hour=1, minute=0),
    },
}

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_WORKER_POOL = "solo"

# ======================================================
# ✉ EMAIL
# ======================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
