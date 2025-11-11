from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('public-questions/', views.public_questions, name='public_questions'),
    path('pricing/', views.pricing, name='pricing'),
    path('lawyers/', views.lawyers_list, name='lawyers_list'),

    # Auth
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Registration
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/lawyer/', views.register_lawyer, name='register_lawyer'),

    # Logged-in landing
    path('my-questions/', views.my_questions, name='my_questions'),
]
