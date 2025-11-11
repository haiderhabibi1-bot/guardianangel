from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),
    path("public-questions/", views.public_questions, name="public_questions"),
    path("lawyers/", views.lawyers_list, name="lawyers_list"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/lawyer/", views.register_lawyer, name="register_lawyer"),
    path("my-questions/", views.my_questions, name="my_questions"),
]
