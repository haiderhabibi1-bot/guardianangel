from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect

from .models import (
    CustomerProfile,
    LawyerProfile,
    PublicQuestion,
)


# HOME / ABOUT ---------------------------------------------------------------

def home(request):
    # Your "About Us" content lives in about.html and is styled via base.html.
    return render(request, "about.html")


# PUBLIC QUESTIONS -----------------------------------------------------------

def public_questions(request):
    """
    Show answered public questions.

    Template: public_questions.html
    Expects 'questions' with .question_text and .answer.
    """
    questions = (
        PublicQuestion.objects.filter(is_answered=True)
        .order_by("-created_at")
    )
    return render(request, "public_questions.html", {"questions": questions})


# PRICING --------------------------------------------------------------------

def pricing(request):
    return render(request, "pricing.html")


# LAWYERS LIST ---------------------------------------------------------------

def lawyers_list(request):
    """
    Show all approved lawyers.

    Template: lawyers_list.html
    Expects 'lawyers' queryset with:
      - lawyer.name (derived from user)
      - speciality
      - years_of_practice
      - bio
      - fee_per_chat
    """
    lawyers = (
        LawyerProfile.objects.filter(is_approved=True)
        .select_related("user")
        .order_by("user__last_name", "user__first_name", "user__username")
    )
    return render(request, "lawyers_list.html", {"lawyers": lawyers})


# REGISTRATION ---------------------------------------------------------------

@transaction.atomic
def register_customer(request):
    """
    Register a regular customer.
    Uses register_customer.html (same layout & wording).
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if username and password:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email or "",
            )
            CustomerProfile.objects.create(user=user)
            login(request, user)
            return redirect("my_questions")

    return render(request, "register_customer.html")


@transaction.atomic
def register_lawyer(request):
    """
    Register a lawyer.
    Uses register_lawyer.html (same layout & wording).
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        speciality = request.POST.get("speciality", "").strip()
        years_raw = request.POST.get("years_of_practice", "").strip()

        try:
            years_of_practice = int(years_raw) if years_raw else 0
        except ValueError:
            years_of_practice = 0

        if username and password:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email or "",
            )
            LawyerProfile.objects.create(
                user=user,
                speciality=speciality,
                years_of_practice=years_of_practice,
            )
            login(request, user)
            return redirect("my_questions")

    return render(request, "register_lawyer.html")


# MY QUESTIONS ---------------------------------------------------------------

@login_required
def my_questions(request):
    """
    After login, customers land here.

    - Customers: see their own public questions (if you later add creation).
    - Lawyers: for now, show answered public questions (read-only).
    """
    customer = getattr(request.user, "customer_profile", None)
    lawyer = getattr(request.user, "lawyer_profile", None)

    if customer:
        questions = (
            PublicQuestion.objects.filter(customer=customer)
            .order_by("-created_at")
        )
    elif lawyer:
        questions = (
            PublicQuestion.objects.filter(is_answered=True)
            .order_by("-created_at")
        )
    else:
        questions = PublicQuestion.objects.none()

    return render(request, "my_questions.html", {"questions": questions})


# CUSTOM 404 (optional hook) -------------------------------------------------

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)
