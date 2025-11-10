from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Core pages
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),

    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),

    # Registration
    path("register/", views.register, name="register"),
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/lawyer/", views.register_lawyer, name="register_lawyer"),

    # Profiles & settings
    path("customer/profile/", views.customer_profile, name="customer_profile"),
    path("customer/settings/", views.customer_settings, name="customer_settings"),
    path("lawyer/profile/", views.lawyer_profile, name="lawyer_profile"),
    path("lawyer/settings/", views.lawyer_settings, name="lawyer_settings"),

    # Public Q&A
    path("public-questions/", views.public_questions, name="public_questions"),
    path("public-questions/ask/", views.ask_public_question, name="ask_public_question"),
    path(
        "public-questions/<int:question_id>/answer/",
        views.answer_public_question,
        name="answer_public_question",
    ),
]
