import os
from pathlib import Path

# ========================================
# BASE SETTINGS
# ========================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key and debug from environment
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# ========================================
# ALLOWED HOSTS
# ========================================
# If ALLOWED_HOSTS env variable exists, use it (comma-separated).
# Otherwise, use the stable default list.
env_allowed_hosts = os.environ.get("ALLOWED_HOSTS")

if env_allowed_hosts:
    ALLOWED_HOSTS = [
        host.strip()
        for host in env_allowed_hosts.split(",")
        if host.strip()
    ]
else:
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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static files
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
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# ========================================
# INTERNATIONALIZATION
# ========================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True

# ========================================
# STATIC FILES
# ========================================
STATIC_URL = "/static/"

# Project-level static directory (where core/css/style.css lives)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Where collectstatic puts files on Render
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise for efficient static serving
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ========================================
# MEDIA FILES (optional)
# ========================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========================================
# DEFAULT PRIMARY KEY FIELD
# ========================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========================================
# LOGGING (optional)
# ========================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
