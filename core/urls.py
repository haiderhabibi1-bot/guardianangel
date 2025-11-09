from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/lawyer/', views.register_lawyer, name='register_lawyer'),
    path('general-questions/', views.general_questions, name='general_questions'),
    path('lawyers/', views.lawyers_list, name='lawyers_list'),
]
