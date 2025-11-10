from django.urls import path
from . import views

urlpatterns = [
    # Main “Ask a Lawyer” page (already working)
    path("", views.home, name="home"),

    # Public questions listing
    path("public-questions/", views.public_questions, name="public_questions"),

    # Approved lawyers directory
    path("lawyers/", views.lawyers_list, name="lawyers_list"),

    # Pricing page
    path("pricing/", views.pricing, name="pricing"),

    # Registration landing + specific flows
    path("register/", views.register_landing, name="register"),
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/lawyer/", views.register_lawyer, name="register_lawyer"),
]
