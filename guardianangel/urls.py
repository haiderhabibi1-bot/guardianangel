import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

ADMIN_URL = os.getenv('DJANGO_ADMIN_URL', 'ga-admin-47821/')

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path('', include('core.urls')),  # 👈 this sends "/" and everything else to your app
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
