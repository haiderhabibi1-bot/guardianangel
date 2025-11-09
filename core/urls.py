from django.urls import path
from . import views

urlpatterns = [
path('', views.home, name='home'),

# Authentication
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),

# Registration
path('register/customer/', views.register_customer, name='register_customer'),
path('register/lawyer/', views.register_lawyer, name='register_lawyer'),

# Main features
path('general-questions/', views.general_questions, name='general_questions'),
path('lawyers/', views.lawyers_list, name='lawyers_list'),
]
