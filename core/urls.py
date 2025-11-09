from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Ask a lawyer page (already working)
    path("public-questions/", views.public_questions, name="public_questions"),
    path("pricing/", views.pricing, name="pricing"),
    path("register/", views.register_landing, name="register"),
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/lawyer/", views.register_lawyer, name="register_lawyer"),
    path("lawyers/", views.lawyers_list, name="lawyers_list"),
]
