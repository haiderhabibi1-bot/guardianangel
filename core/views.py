from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    LoginForm,
    QuestionForm,
    AnswerForm,
)
from .models import CustomerProfile, LawyerProfile, PublicQuestion, PublicAnswer


# ------------------------------------
# HOME PAGE
# ------------------------------------
def home(request):
    return render(request, "home.html")


# ------------------------------------
# ABOUT PAGE
# ------------------------------------
def about(request):
    return render(request, "about.html")


# ------------------------------------
# PUBLIC QUESTIONS (visible to everyone)
# ------------------------------------
def public_questions(request):
    questions = PublicQuestion.objects.all().order_by("-created_at")
    return render(request, "public_questions.html", {"questions": questions})


# ------------------------------------
# ASK QUESTION (Customer must be logged in)
# ------------------------------------
@login_required
def ask_question(request):
    if hasattr(request.user, "customerprofile"):
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.customer = request.user.customerprofile
                question.save()
                messages.success(request, "Your question was submitted successfully!")
                return redirect("public_questions")
        else:
            form = QuestionForm()
        return render(request, "ask_question.html", {"form": form})
    else:
        messages.error(request, "Only customers can ask questions.")
        return redirect("home")


# ------------------------------------
# ANSWER QUESTION (Lawyer must be logged in)
# ------------------------------------
@login_required
def answer_question(request, question_id):
    if hasattr(request.user, "lawyerprofile"):
        question = get_object_or_404(PublicQuestion, id=question_id)
        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = question
                answer.lawyer = request.user.lawyerprofile
                answer.save()
                messages.success(request, "Your answer was posted successfully!")
                return redirect("public_questions")
        else:
            form = AnswerForm()
        return render(
            request,
            "answer_question.html",
            {"form": form, "question": question},
        )
    else:
        messages.error(request, "Only lawyers can answer questions.")
        return redirect("home")


# ------------------------------------
# CUSTOMER REGISTRATION
# ------------------------------------
def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.create(user=user)
            messages.success(request, "Customer account created successfully.")
            return redirect("login")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register_customer.html", {"form": form})


# ------------------------------------
# LAWYER REGISTRATION
# ------------------------------------
def register_lawyer(request):
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            LawyerProfile.objects.create(user=user)
            messages.success(request, "Lawyer account created successfully.")
            return redirect("login")
    else:
        form = LawyerRegistrationForm()
    return render(request, "register_lawyer.html", {"form": form})


# ------------------------------------
# LOGIN
# ------------------------------------
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


# ------------------------------------
# LOGOUT
# ------------------------------------
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


# ------------------------------------
# LAWYERS LIST
# ------------------------------------
def lawyers_list(request):
    lawyers = LawyerProfile.objects.all().order_by("user__username")
    return render(request, "lawyers_list.html", {"lawyers": lawyers})


# ------------------------------------
# PRICING PAGE
# ------------------------------------
def pricing(request):
    return render(request, "pricing.html")


# ------------------------------------
# 404 HANDLER (optional for polish)
# ------------------------------------
def custom_404(request, exception=None):
    return render(request, "404.html", status=404)
