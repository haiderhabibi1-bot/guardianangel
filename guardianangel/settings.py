import os
from pathlib import Path

# ========================================
# BASE SETTINGS
# ========================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key and debug from environment (Render)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# ========================================
# ALLOWED HOSTS
# ========================================
# Includes Render, localhost, and your custom domain
ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
    "guardianangelconsulting.ca",
    "www.guardianangelconsulting.ca",
]

# ========================================
# APPLICATIONS
# ========================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

# ========================================
# MIDDLEWARE
# ========================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files efficiently
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "guardianangel.urls"

# ========================================
# TEMPLATES
# ========================================
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

WSGI_APPLICATION = "guardianangel.wsgi.application"

# ========================================
# DATABASE
# ========================================
# Default: SQLite (can replace with PostgreSQL later)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ========================================
# PASSWORD VALIDATION
# ========================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================================
# LOCALIZATION
# ========================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True

# ========================================
# STATIC FILES
# ========================================
STATIC_URL = "/static/"

# Project-level static directory (your CSS, JS, etc.)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Directory for Render’s collectstatic command
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise handles static file compression and caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ========================================
# MEDIA FILES (optional, for uploads)
# ========================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========================================
# DEFAULTS
# ========================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========================================
# LOGGING (optional)
# ========================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
