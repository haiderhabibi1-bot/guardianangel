from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import IntegrityError

# HOME

def home(request):
    return render(request, "home.html")

# SIMPLE PAGES

def pricing(request):
    return render(request, "pricing.html")


def public_questions(request):
    # For now: simple "no answered questions yet" message.
    # (Safe: does not hit any missing tables.)
    context = {
        "questions": [],
    }
    return render(request, "public_questions.html", context)


def lawyers_list(request):
    # For now: placeholder list, to be wired to real LawyerProfile later.
    lawyers = []
    return render(request, "lawyers_list.html", {"lawyers": lawyers})


# AUTH

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")
    # If someone hits /logout/ via GET, just send them home.
    return redirect("home")


def register_customer(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                messages.success(request, "Account created. Please log in.")
                return redirect("login")
            except IntegrityError:
                messages.error(request, "Username already taken.")

    return render(request, "register_customer.html")


def register_lawyer(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                # Mark as staff just so we can distinguish later if needed.
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=True,
                )
                messages.success(request, "Lawyer account created. Please log in.")
                return redirect("login")
            except IntegrityError:
                messages.error(request, "Username already taken.")

    return render(request, "register_lawyer.html")


# CUSTOMER "MY QUESTIONS" PLACEHOLDER

@login_required
def my_questions(request):
    # Placeholder; no DB calls that can blow up.
    return render(request, "my_questions.html")
