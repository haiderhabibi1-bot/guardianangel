import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.management.utils import get_random_secret_key

# Load environment variables (optional, safe for Render)
load_dotenv()

# -------------------------------------------------------
# BASE DIRECTORY
# -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------
# SECURITY SETTINGS
# -------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "guardianangelconsulting.ca",
    "www.guardianangelconsulting.ca",
    "guardianangel-w7fo.onrender.com",
    "localhost",
    "127.0.0.1"
]

# -------------------------------------------------------
# INSTALLED APPS
# -------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your core app
    "core",
]

# -------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------------------------
# URL CONFIGURATION
# -------------------------------------------------------
ROOT_URLCONF = "guardianangel.urls"

# -------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],  # points to your core/templates/
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.global_settings",  # optional if used
            ],
        },
    },
]

# -------------------------------------------------------
# WSGI APPLICATION
# -------------------------------------------------------
WSGI_APPLICATION = "guardianangel.wsgi.application"

# -------------------------------------------------------
# DATABASE
# -------------------------------------------------------
# Render uses PostgreSQL — adjust if you’re on SQLite locally
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ⚠️ Remove STATICFILES_DIRS if present
# STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------------------------
# DEFAULT AUTO FIELD
# -------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------
# AUTHENTICATION / LOGIN
# -------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# -------------------------------------------------------
# EMAIL CONFIGURATION (for notifications)
# -------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# -------------------------------------------------------
# RENDER DEPLOYMENT (SECURITY HEADERS)
# -------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# -------------------------------------------------------
# LOGGING (optional but recommended)
# -------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
