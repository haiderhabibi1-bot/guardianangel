from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    CustomerSettingsForm,
    LawyerSettingsForm,
    PublicQuestionForm,
    PublicAnswerForm,
)
from .models import Profile, PublicQuestion, PublicAnswer


# ========= REGISTRATION =========

def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login + redirect to their profile
            login(request, user)
            messages.success(request, "Your customer account has been created.")
            return redirect("customer_profile")
    else:
        form = CustomerRegistrationForm()
    return render(request, "auth/register_customer.html", {"form": form})


def register_lawyer(request):
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Notify admin for approval
            approval_email = getattr(settings, "LAWYER_APPROVAL_EMAIL", None)
            if approval_email:
                send_mail(
                    subject="New Lawyer Registration Pending Approval",
                    message=(
                        f"A new lawyer has registered.\n\n"
                        f"Username: {user.username}\n"
                        f"Email: {user.email}\n"
                        f"Full name: {user.profile.full_name}\n"
                        f"Bar number: {user.profile.bar_number}\n\n"
                        f"Log in to the admin panel to approve them."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[approval_email],
                    fail_silently=True,
                )
            messages.success(
                request,
                "Your registration has been received. You will be notified once approved.",
            )
            return redirect("login")
    else:
        form = LawyerRegistrationForm()
    return render(request, "auth/register_lawyer.html", {"form": form})


# ========= DASHBOARDS / PROFILES =========

@login_required
def customer_profile(request):
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")
    return render(request, "profiles/customer_profile.html", {"profile": profile})


@login_required
def lawyer_profile(request):
    profile = request.user.profile
    if not profile.is_lawyer:
        return redirect("home")
    if not profile.is_approved:
        return render(request, "profiles/lawyer_pending.html", {"profile": profile})
    return render(request, "profiles/lawyer_profile.html", {"profile": profile})


# ========= SETTINGS =========

@login_required
def customer_settings(request):
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    if request.method == "POST":
        form = CustomerSettingsForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings have been updated.")
            return redirect("customer_settings")
    else:
        form = CustomerSettingsForm(user=request.user)

    return render(request, "profiles/customer_settings.html", {"form": form})


@login_required
def lawyer_settings(request):
    profile = request.user.profile
    if not profile.is_lawyer:
        return redirect("home")

    if request.method == "POST":
        form = LawyerSettingsForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings have been updated.")
            return redirect("lawyer_settings")
    else:
        form = LawyerSettingsForm(user=request.user)

    return render(request, "profiles/lawyer_settings.html", {"form": form})


# ========= PUBLIC Q&A =========

@login_required
def ask_public_question(request):
    """Only customers can ask. Question is anonymous publicly."""
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    if request.method == "POST":
        form = PublicQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.customer = request.user
            q.save()
            messages.success(
                request,
                "Your question has been submitted. It will appear once answered by a lawyer.",
            )
            return redirect("public_questions")
    else:
        form = PublicQuestionForm()

    return render(request, "public/ask_public_question.html", {"form": form})


@login_required
def answer_public_question(request, question_id):
    """Only approved lawyers can answer unanswered questions."""
    profile = request.user.profile
    if not (profile.is_lawyer and profile.is_approved):
        return redirect("home")

    question = get_object_or_404(PublicQuestion, id=question_id)

    # If already answered, no double answers
    if question.is_answered:
        return redirect("public_questions")

    if request.method == "POST":
        form = PublicAnswerForm(request.POST)
        if form.is_valid():
            ans = form.save(commit=False)
            ans.question = question
            ans.lawyer = request.user
            ans.save()
            messages.success(request, "Answer submitted.")
            return redirect("public_questions")
    else:
        form = PublicAnswerForm()

    return render(
        request,
        "public/answer_public_question.html",
        {"form": form, "question": question},
    )


def public_questions(request):
    """
    Public page: shows ONLY answered questions.
    Anonymity: no usernames shown.
    """
    questions = (
        PublicQuestion.objects.filter(answer__isnull=False)
        .select_related("answer")
        .order_by("-answer__created_at")
    )
    return render(request, "public/public_questions.html", {"questions": questions})
