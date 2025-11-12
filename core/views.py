from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from .forms import (
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    BillingProfileForm,
    LawyerProfileSettingsForm,
    PublicQuestionForm,
    PublicAnswerForm,
    ChatMessageForm,
)
from .models import (
    Profile,
    BillingProfile,
    LawyerProfile,
    PublicQuestion,
    PublicAnswer,
    Chat,
    ChatMessage,
)


# ---------- Public pages ----------

def home(request):
    return render(request, "home.html")


def pricing(request):
    return render(request, "pricing.html")


def lawyers_list(request):
    lawyers = LawyerProfile.objects.filter(is_approved=True).order_by("full_name")
    return render(request, "lawyers_list.html", {"lawyers": lawyers})


# ---------- Registration & Auth ----------

def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, user_type="customer")
            BillingProfile.objects.create(user=user)
            login(request, user)
            return redirect("my_questions")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register_customer.html", {"form": form})


def register_lawyer(request):
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            lp = LawyerProfile.objects.create(
                user=user,
                full_name=form.cleaned_data.get("full_name") or user.username,
                specialty=form.cleaned_data.get("specialty", ""),
                years_of_practice=form.cleaned_data.get("years_of_practice") or 0,
                bar_number=form.cleaned_data.get("bar_number", ""),
            )
            Profile.objects.create(user=user, user_type="lawyer", lawyer_profile=lp)
            BillingProfile.objects.create(user=user)
            login(request, user)
            return redirect("my_customers")
    else:
        form = LawyerRegistrationForm()
    return render(request, "register_lawyer.html", {"form": form})


class GuardianLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return reverse("home")
        if profile.user_type == "lawyer":
            return reverse("my_customers")
        return reverse("my_questions")


class GuardianLogoutView(LogoutView):
    next_page = reverse_lazy("home")


# ---------- Settings ----------

@login_required
def settings_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, user_type="customer")

    billing_profile, _ = BillingProfile.objects.get_or_create(user=request.user)

    lawyer_profile_form = None
    if profile.user_type == "lawyer" and profile.lawyer_profile:
        if request.method == "POST":
            lawyer_profile_form = LawyerProfileSettingsForm(
                request.POST, instance=profile.lawyer_profile, prefix="lawyer"
            )
            if lawyer_profile_form.is_valid():
                lawyer_profile_form.save()
        else:
            lawyer_profile_form = LawyerProfileSettingsForm(
                instance=profile.lawyer_profile, prefix="lawyer"
            )

    if request.method == "POST":
        billing_form = BillingProfileForm(
            request.POST, instance=billing_profile, prefix="billing"
        )
        if billing_form.is_valid():
            billing_form.save()
            messages.success(request, "Settings updated.")
            return redirect("settings")
    else:
        billing_form = BillingProfileForm(
            instance=billing_profile, prefix="billing"
        )

    return render(
        request,
        "settings.html",
        {
            "billing_form": billing_form,
            "lawyer_profile_form": lawyer_profile_form,
        },
    )


# ---------- Public Questions ----------

def public_questions(request):
    answered = (
        PublicQuestion.objects.filter(status=PublicQuestion.STATUS_ANSWERED)
        .select_related("answer")
        .order_by("-created_at")
    )

    customer_questions = None
    question_form = None

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

        if profile and profile.user_type == "customer":
            customer_questions = (
                PublicQuestion.objects.filter(customer=request.user)
                .select_related("answer")
                .order_by("-created_at")
            )

            asked_free = PublicQuestion.objects.filter(
                customer=request.user, is_free=True
            ).count()
            remaining = max(0, 2 - asked_free)

            if request.method == "POST":
                question_form = PublicQuestionForm(request.POST)
                if question_form.is_valid():
                    if remaining <= 0:
                        messages.error(
                            request,
                            "You have already used your two free public questions.",
                        )
                    else:
                        pq = question_form.save(commit=False)
                        pq.customer = request.user
                        pq.is_free = True
                        pq.save()
                        messages.success(
                            request,
                            "Your question has been submitted.",
                        )
                        return redirect("public_questions")
            else:
                question_form = PublicQuestionForm()

    context = {
        "answered_questions": answered,
        "customer_questions": customer_questions,
        "question_form": question_form,
    }
    return render(request, "public_questions.html", context)


@login_required
def answer_public_question(request, question_id):
    # Only approved lawyers
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect("public_questions")

    if profile.user_type != "lawyer" or not profile.lawyer_profile:
        messages.error(request, "Only lawyers can answer.")
        return redirect("public_questions")

    question = get_object_or_404(
        PublicQuestion,
        pk=question_id,
        status=PublicQuestion.STATUS_PENDING,
    )

    if request.method == "POST":
        form = PublicAnswerForm(request.POST)
        if form.is_valid():
            PublicAnswer.objects.create(
                question=question,
                lawyer=profile.lawyer_profile,
                answer_text=form.cleaned_data["answer_text"],
            )
            question.status = PublicQuestion.STATUS_ANSWERED
            question.save(update_fields=["status"])
            messages.success(request, "Answer posted.")
            return redirect("public_questions")
    else:
        form = PublicAnswerForm()

    return render(
        request,
        "answer_public_question.html",
        {"question": question, "form": form},
    )


# ---------- Customer My Questions ----------

@login_required
def my_questions(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("home")

    if profile.user_type != "customer":
        return redirect("home")

    public_questions_qs = (
        PublicQuestion.objects.filter(customer=request.user)
        .select_related("answer")
        .order_by("-created_at")
    )

    chats = Chat.objects.filter(customer=request.user).select_related("lawyer")

    return render(
        request,
        "my_questions.html",
        {
            "public_questions": public_questions_qs,
            "chats": chats,
        },
    )


# ---------- Lawyer My Customers ----------

@login_required
def my_customers(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("home")

    if profile.user_type != "lawyer" or not profile.lawyer_profile:
        return redirect("home")

    chats = (
        Chat.objects.filter(lawyer=profile.lawyer_profile)
        .select_related("customer")
        .order_by("-created_at")
    )

    return render(request, "my_customers.html", {"chats": chats})


# ---------- Chat ----------

@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("home")

    if profile.user_type == "customer":
        if chat.customer != request.user:
            return redirect("home")
    elif profile.user_type == "lawyer":
        if chat.lawyer != profile.lawyer_profile:
            return redirect("home")
    else:
        return redirect("home")

    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            ChatMessage.objects.create(
                chat=chat,
                sender=request.user,
                content=form.cleaned_data["content"],
            )
            return redirect("chat_view", chat_id=chat.id)
    else:
        form = ChatMessageForm()

    messages_qs = chat.messages.select_related("sender")

    return render(
        request,
        "chat.html",
        {
            "chat": chat,
            "form": form,
            "messages": messages_qs,
        },
    )
