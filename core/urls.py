# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # If we ever include core.urls again, this will just show the home page.
    path('', views.home, name='core_home'),
]
