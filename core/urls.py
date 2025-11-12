from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),
    path("public-questions/", views.public_questions, name="public_questions"),
    path("lawyers/", views.lawyers_list, name="lawyers_list"),

    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/lawyer/", views.register_lawyer, name="register_lawyer"),

    path("login/", views.GuardianLoginView.as_view(), name="login"),
    path("logout/", views.GuardianLogoutView.as_view(), name="logout"),

    path("settings/", views.settings_view, name="settings"),

    path("my-questions/", views.my_questions, name="my_questions"),
    path("my-customers/", views.my_customers, name="my_customers"),
    path("chat/<int:chat_id>/", views.chat_view, name="chat_view"),

    path(
        "public-questions/<int:question_id>/answer/",
        views.answer_public_question,
        name="answer_public_question",
    ),
]
