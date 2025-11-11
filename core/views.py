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
    ChatMessageForm,
)
from .models import (
    Profile,
    BillingProfile,
    PublicQuestion,
    PublicAnswer,
    Chat,
    ChatMessage,
)


# =========================
# CORE PAGES
# =========================

def home(request):
    return render(request, "home.html")


def pricing(request):
    return render(request, "pricing.html")


def register(request):
    # Legacy safety redirect
    return redirect("register_customer")


# =========================
# REGISTRATION
# =========================

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
                "Your registration has been received. "
                "You will be granted access once approved.",
            )
            return redirect("login")
    else:
        form = LawyerRegistrationForm()

    return render(request, "register_lawyer.html", {"form": form})


# =========================
# PROFILES / DASHBOARDS
# =========================

@login_required
def customer_profile(request):
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    billing = getattr(request.user, "billing", None)
    return render(
        request,
        "profiles/customer_profile.html",
        {"profile": profile, "billing": billing},
    )


@login_required
def lawyer_profile(request):
    profile = request.user.profile
    if not profile.is_lawyer:
        return redirect("home")

    if not profile.is_approved:
        return render(
            request,
            "profiles/lawyer_pending.html",
            {"profile": profile},
        )

    billing = getattr(request.user, "billing", None)
    return render(
        request,
        "profiles/lawyer_profile.html",
        {"profile": profile, "billing": billing},
    )


# =========================
# SETTINGS
# =========================

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


# =========================
# PUBLIC Q&A
# =========================

@login_required
def ask_public_question(request):
    """
    Customers get up to 2 free public questions.
    """
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    existing_count = PublicQuestion.objects.filter(
        customer=request.user
    ).count()
    if existing_count >= 2:
        messages.error(
            request,
            "You have used your two free public questions.",
        )
        return redirect("public_questions")

    if request.method == "POST":
        form = PublicQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.customer = request.user
            q.save()
            messages.success(
                request,
                "Your question has been submitted. "
                "It will appear once answered by a lawyer.",
            )
            return redirect("public_questions")
    else:
        form = PublicQuestionForm()

    return render(
        request,
        "public/ask_public_question.html",
        {"form": form},
    )


@login_required
def answer_public_question(request, question_id):
    """
    Approved lawyers can answer any pending question.
    """
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
        "public/answer_public_question.html",
        {"form": form, "question": question},
    )


def public_questions(request):
    """
    Public page:
    - Always shows all answered questions.
    - Logged-in customers additionally see ONLY their own pending questions.
    """
    answered = (
        PublicQuestion.objects.filter(answer__isnull=False)
        .select_related("answer")
        .order_by("-answer__created_at")
    )

    customer_pending = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
        if profile and profile.is_customer:
            customer_pending = (
                PublicQuestion.objects.filter(
                    customer=request.user,
                    answer__isnull=True,
                )
                .order_by("-created_at")
            )

    return render(
        request,
        "public/public_questions.html",
        {
            "questions": answered,
            "customer_pending": customer_pending,
        },
    )


# =========================
# LAWYERS LIST
# =========================

def lawyers_list(request):
    """
    Visible to everyone:
    - Shows approved lawyers with name, years of practice, bio, fee.
    - 'Start chat' behavior handled in template + start_chat_with_lawyer view.
    """
    lawyers = (
        Profile.objects.filter(
            role=Profile.ROLE_LAWYER,
            is_approved=True,
        )
        .select_related("user")
        .order_by("full_name", "user__username")
    )
    return render(request, "lawyers_list.html", {"lawyers": lawyers})


# =========================
# CHATS
# =========================

@login_required
def start_chat_with_lawyer(request, lawyer_id):
    """
    Start chat from Lawyers List.
    - If not customer: redirect to register_customer.
    - If already has chat: go directly to chat.
    - Simulated payment: confirm screen -> POST to create chat.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("register_customer")

    if not profile.is_customer:
        return redirect("register_customer")

    lawyer_profile = get_object_or_404(
        Profile,
        user__id=lawyer_id,
        role=Profile.ROLE_LAWYER,
        is_approved=True,
    )
    lawyer = lawyer_profile.user

    chat, created = Chat.objects.get_or_create(
        customer=request.user,
        lawyer=lawyer,
    )

    if not created:
        # Already has an active chat: go straight to it
        return redirect("chat_detail", chat_id=chat.id)

    # Simple confirmation step in UI (payment placeholder)
    if request.method == "POST":
        messages.success(
            request,
            "Your payment has been recorded and your chat is now active.",
        )
        return redirect("chat_detail", chat_id=chat.id)

    return render(
        request,
        "chats/start_chat_payment.html",
        {
            "lawyer_profile": lawyer_profile,
            "chat": chat,
        },
    )


@login_required
def my_questions(request):
    """
    Customer: list of chats with lawyers.
    """
    profile = request.user.profile
    if not profile.is_customer:
        return redirect("home")

    chats = Chat.objects.filter(customer=request.user).select_related("lawyer__profile")
    return render(
        request,
        "chats/my_questions.html",
        {"chats": chats},
    )


@login_required
def my_customers(request):
    """
    Lawyer: list of customers they have chats with.
    """
    profile = request.user.profile
    if not profile.is_lawyer:
        return redirect("home")

    chats = Chat.objects.filter(lawyer=request.user).select_related(
        "customer__profile"
    )
    return render(
        request,
        "chats/my_customers.html",
        {"chats": chats},
    )


@login_required
def chat_detail(request, chat_id):
    """
    Shared chat view for customer & lawyer.
    Only participants can access.
    """
    chat = get_object_or_404(Chat, id=chat_id)

    if request.user != chat.customer and request.user != chat.lawyer:
        return redirect("home")

    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.chat = chat
            msg.sender = request.user
            msg.save()
            return redirect("chat_detail", chat_id=chat.id)
    else:
        form = ChatMessageForm()

    messages_qs = chat.messages.select_related("sender")
    return render(
        request,
        "chats/chat_detail.html",
        {
            "chat": chat,
            "messages": messages_qs,
            "form": form,
        },
    )
