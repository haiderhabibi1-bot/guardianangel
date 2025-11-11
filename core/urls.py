from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),

    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),

    # Registration
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/lawyer/", views.register_lawyer, name="register_lawyer"),

    # Profiles
    path("profile/customer/", views.customer_profile, name="customer_profile"),
    path("profile/lawyer/", views.lawyer_profile, name="lawyer_profile"),

    # Settings
    path(
        "settings/customer/",
        views.customer_settings,
        name="customer_settings",
    ),
    path(
        "settings/lawyer/",
        views.lawyer_settings,
        name="lawyer_settings",
    ),

    # Public Q&A
    path(
        "public-questions/",
        views.public_questions,
        name="public_questions",
    ),
    path(
        "public-questions/ask/",
        views.ask_public_question,
        name="ask_public_question",
    ),
    path(
        "public-questions/<int:question_id>/answer/",
        views.answer_public_question,
        name="answer_public_question",
    ),

    # Lawyers list
    path("lawyers/", views.lawyers_list, name="lawyers_list"),

    # Chats
    path(
        "lawyers/<int:lawyer_id>/start-chat/",
        views.start_chat_with_lawyer,
        name="start_chat_with_lawyer",
    ),
    path("my-questions/", views.my_questions, name="my_questions"),
    path("my-customers/", views.my_customers, name="my_customers"),
    path("chat/<int:chat_id>/", views.chat_detail, name="chat_detail"),
]
