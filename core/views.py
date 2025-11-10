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


# =========================
# CORE PAGES (EXISTING)
# =========================

def home(request):
    # Uses your existing home.html template and layout
    return render(request, "home.html")


def pricing(request):
    # Uses your existing pricing.html template and layout
    return render(request, "pricing.html")


# Keep a simple "Register" entrypoint so your existing navbar link still works.
# This does NOT break anything: it just points "Register" to customer registration.
def register(request):
    return redirect("register_customer")


# =========================
# REGISTRATION
# =========================

def register_customer(request):
    """
    Customer registration:
    - Creates user
    - Creates Profile (role=customer, approved)
    - Creates BillingProfile
    - Logs them in
    - Redirects to their profile
    """
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your customer account has been created.")
            return redirect("customer_profile")
    else:
        form = CustomerRegistrationForm()

    return render(request, "auth/register_customer.html", {"form": form})


def register_lawyer(request):
    """
    Lawyer registration:
    - Creates user
    - Creates Profile (role=lawyer, not approved yet)
    - Creates BillingProfile
    - Sends email notification to admin (your personal email)
    - Does NOT auto-login with full access until approved
    """
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Notify admin for approval (if configured)
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

    return render(request, "auth/register_lawyer.html", {"form": form})


# =========================
# PROFILES / DASHBOARDS
# =========================

@login_required
def customer_profile(request):
    """
    Customer profile page.
    Only accessible for users with customer profile.
    """
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    return render(request, "profiles/customer_profile.html", {"profile": profile})


@login_required
def lawyer_profile(request):
    """
    Lawyer profile / dashboard.
    - If not approved yet: show pending screen.
    - If approved: show dashboard.
    """
    profile = request.user.profile
    if not profile.is_lawyer:
        return redirect("home")

    if not profile.is_approved:
        return render(request, "profiles/lawyer_pending.html", {"profile": profile})

    return render(request, "profiles/lawyer_profile.html", {"profile": profile})


# =========================
# SETTINGS
# =========================

@login_required
def customer_settings(request):
    """
    Customers can edit:
    - username
    - email
    - billing method
    No real name fields: they remain anonymous.
    """
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
    """
    Lawyers can edit:
    - username
    - email
    - billing method
    They CANNOT edit:
    - name
    - bar number
    - other verified details
    """
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


# =========================
# PUBLIC Q&A
# =========================

@login_required
def ask_public_question(request):
    """
    Only customers can submit public questions.
    - Stored as linked to the customer (internally)
    - Displayed anonymously
    - Only shown once answered by an approved lawyer
    """
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    if request.method == "POST":
        form = PublicQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.customer = request.user
            question.save()
            messages.success(
                request,
                "Your question was submitted. It will appear on the public page once a lawyer answers.",
            )
            return redirect("public_questions")
    else:
        form = PublicQuestionForm()

    return render(request, "public/ask_public_question.html", {"form": form})


@login_required
def answer_public_question(request, question_id):
    """
    Only approved lawyers can answer.
    - One answer per question (simple + controlled).
    - Both asker and lawyer are anonymous on the public page.
    """
    profile = request.user.profile
    if not (profile.is_lawyer and profile.is_approved):
        return redirect("home")

    question = get_object_or_404(PublicQuestion, id=question_id)

    # If already answered, no duplicate answers.
    if hasattr(question, "answer"):
        return redirect("public_questions")

    if request.method == "POST":
        form = PublicAnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.lawyer = request.user
            answer.save()
            messages.success(request, "Your answer has been submitted.")
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
    Public page.
    - Shows ONLY questions that have an answer.
    - Does NOT display customer or lawyer identities.
    """
    questions = (
        PublicQuestion.objects.filter(answer__isnull=False)
        .select_related("answer")
        .order_by("-answer__created_at")
    )

    return render(request, "public/public_questions.html", {"questions": questions})
