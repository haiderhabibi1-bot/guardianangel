import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Optional: you can hide the admin panel behind a custom URL path for extra security.
ADMIN_URL = os.getenv('DJANGO_ADMIN_URL', 'ga-admin-47821/')

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),     # Example: yourdomain.com/ga-admin-47821/
    path('', include('core.urls')),       # All app pages come from the core app
]

# This allows uploaded media (like lawyer bar certificates) to work in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
