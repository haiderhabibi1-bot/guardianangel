from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import (
LoginForm,
CustomerRegistrationForm,
LawyerRegistrationForm,
GeneralQuestionForm,
)
from .models import CustomerProfile, LawyerProfile, GeneralQuestion


def home(request):
return render(request, "home.html")


def login_view(request):
if request.method == "POST":
form = LoginForm(request, data=request.POST)
if form.is_valid():
user = form.get_user()
login(request, user)
return redirect("home")
else:
form = LoginForm(request)
return render(request, "login.html", {"form": form})


def logout_view(request):
logout(request)
return redirect("home")


def register_customer(request):
if request.method == "POST":
form = CustomerRegistrationForm(request.POST)
if form.is_valid():
user = form.save()
CustomerProfile.objects.create(user=user)
messages.success(request, "Customer account created. You can now log in.")
return redirect("login")
else:
form = CustomerRegistrationForm()
return render(request, "register_customer.html", {"form": form})


def register_lawyer(request):
if request.method == "POST":
form = LawyerRegistrationForm(request.POST, request.FILES)
if form.is_valid():
form.save() # creates User + LawyerProfile (approved=False)
messages.success(
request,
"Lawyer registration submitted. You will be activated after manual approval."
)
return redirect("login")
else:
form = LawyerRegistrationForm()
return render(request, "register_lawyer.html", {"form": form})


def general_questions(request):
# Show list of public questions + simple form
if request.method == "POST":
form = GeneralQuestionForm(request.POST)
if form.is_valid():
q = form.save(commit=False)
if request.user.is_authenticated:
q.user = request.user
q.is_public = True
q.save()
messages.success(request, "Your question has been submitted.")
return redirect("general_questions")
else:
form = GeneralQuestionForm()

questions = GeneralQuestion.objects.filter(is_public=True).order_by("-created_at")
return render(
request,
"general_questions.html",
{"form": form, "questions": questions},
)


def lawyers_list(request):
lawyers = LawyerProfile.objects.filter(approved=True).select_related("user")
return render(request, "lawyers_list.html", {"lawyers": lawyers})
