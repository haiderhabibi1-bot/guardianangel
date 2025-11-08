import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# CORE SETTINGS
# ========================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
"guardianangelconsulting.ca",
"www.guardianangelconsulting.ca",
"guardian-angel-whcp.onrender.com",
"localhost",
"127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
"https://guardianangelconsulting.ca",
"https://www.guardianangelconsulting.ca",
"https://guardian-angel-whcp.onrender.com",
]

# ========================
# APPLICATIONS
# ========================

INSTALLED_APPS = [
"django.contrib.admin",
"django.contrib.auth",
"django.contrib.contenttypes",
"django.contrib.sessions",
"django.contrib.messages",
"django.contrib.staticfiles",
"core",
]

# ========================
# MIDDLEWARE
# ========================

MIDDLEWARE = [
"django.middleware.security.SecurityMiddleware",
"django.contrib.sessions.middleware.SessionMiddleware",
"django.middleware.common.CommonMiddleware",
"django.middleware.csrf.CsrfViewMiddleware",
"django.contrib.auth.middleware.AuthenticationMiddleware",
"django.contrib.messages.middleware.MessageMiddleware",
"django.middleware.clickjacking.XFrameOptionsMiddleware",
"core.middleware.security.SecurityHeadersMiddleware",
"core.middleware.ratelimit.SimpleRateLimitMiddleware",
]

ROOT_URLCONF = "guardianangel.urls"

# ========================
# TEMPLATES
# ========================

TEMPLATES = [
{
"BACKEND": "django.template.backends.django.DjangoTemplates",
"DIRS": [BASE_DIR / "core" / "templates"],
"APP_DIRS": True,
"OPTIONS": {
"context_processors": [
"django.template.context_processors.debug",
"django.template.context_processors.request",
"django.contrib.auth.context_processors.auth",
"django.contrib.messages.context_processors.messages",
"core.context_processors.user_roles", # must exist in core/context_processors.py
],
},
},
]

WSGI_APPLICATION = "guardianangel.wsgi.application"

# ========================
# DATABASE
# ========================

DATABASES = {
"default": {
"ENGINE": "django.db.backends.sqlite3",
"NAME": BASE_DIR / "db.sqlite3",
}
}

# ========================
# PASSWORD VALIDATION
# ========================

AUTH_PASSWORD_VALIDATORS = [
{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================
# INTERNATIONALIZATION
# ========================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True

# ========================
# STATIC & MEDIA
# ========================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
BASE_DIR / "core" / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========================
# EMAIL CONFIGURATION
# ========================

EMAIL_BACKEND = os.getenv(
"DJANGO_EMAIL_BACKEND",
"django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1")

DEFAULT_FROM_EMAIL = os.getenv(
"DJANGO_DEFAULT_FROM_EMAIL",
"no-reply@guardianangelconsulting.ca"
)

# Where lawyer registration notifications go
LAWYER_REGISTRATION_NOTIFY_EMAIL = os.getenv(
"LAWYER_REGISTRATION_NOTIFY_EMAIL",
DEFAULT_FROM_EMAIL,
)

# ========================
# STRIPE (OPTIONAL)
# ========================

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# ========================
# AUTH / LOGIN
# ========================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ========================
# RATE LIMIT
# ========================

# Format: "seconds:requests"
RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "60:1000")

# ========================
# SECURITY HARDENING
# ========================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
X_FRAME_OPTIONS = "DENY"
