from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    CustomerSettingsForm,
    LawyerSettingsForm,
    PublicQuestionForm,
    PublicAnswerForm,
)
from .models import Profile, PublicQuestion, PublicAnswer


def home(request):
    return render(request, "home.html")


def pricing(request):
    return render(request, "pricing.html")


def register(request):
    return redirect("register_customer")


def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your customer account has been created.")
            return redirect("customer_profile")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register_customer.html", {"form": form})


def register_lawyer(request):
    # CHANGED: include request.FILES for bar_certificate upload
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            approval_email = getattr(settings, "LAWYER_APPROVAL_EMAIL", None)
            if approval_email:
                profile = user.profile
                send_mail(
                    subject="New Lawyer Registration Pending Approval",
                    message=(
                        "A new lawyer has registered and is pending approval.\n\n"
                        f"Username: {user.username}\n"
                        f"Email: {user.email}\n"
                        f"Full name: {profile.full_name}\n"
                        f"Bar number: {profile.bar_number}\n\n"
                        "Log in to the admin panel to review and approve."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[approval_email],
                    fail_silently=True,
                )

            messages.success(
                request,
                "Your registration has been received. You will be granted access once approved.",
            )
            return redirect("login")
    else:
        form = LawyerRegistrationForm()

    return render(request, "register_lawyer.html", {"form": form})


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


@login_required
def ask_public_question(request):
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

    return render(request, "ask_public_question.html", {"form": form})


@login_required
def answer_public_question(request, question_id):
    profile = request.user.profile
    if not (profile.is_lawyer and profile.is_approved):
        return redirect("home")

    question = get_object_or_404(PublicQuestion, id=question_id)

    if hasattr(question, "answer"):
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
        "answer_public_question.html",
        {"form": form, "question": question},
    )


def public_questions(request):
    questions = (
        PublicQuestion.objects.filter(answer__isnull=False)
        .select_related("answer")
        .order_by("-answer__created_at")
    )
    return render(request, "public_questions.html", {"questions": questions})
