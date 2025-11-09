from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Send all main routes to the core app
    path('', include('core.urls')),
]
