from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # User Authentication
    path('login/', views.profile, name='login'),  # placeholder for now
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/lawyer/', views.register_lawyer, name='register_lawyer'),

    # Lawyer Listings
    path('lawyers/', views.lawyers_list, name='lawyers_list'),

    # Optional placeholder (prevents crash if referenced)
    path('lawyer/subscribe/', views.lawyer_subscribe, name='lawyer_subscribe'),

    # Profile page
    path('profile/', views.profile, name='profile'),
]
