from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (
    CustomerProfile,
    LawyerProfile,
    PublicQuestion,
    PublicAnswer,
)
from .forms import (
    LoginForm,
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    PublicQuestionForm,
    PublicAnswerForm,
)


# -------- Static-style pages (UI unchanged) --------

def home(request):
    return render(request, "home.html")


def pricing(request):
    return render(request, "pricing.html")


# -------- Auth --------

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()
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
            login(request, user)
            return redirect("home")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register_customer.html", {"form": form})


def register_lawyer(request):
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            LawyerProfile.objects.create(
                user=user,
                bar_certificate=form.cleaned_data.get("bar_certificate"),
            )
            login(request, user)
            return redirect("home")
    else:
        form = LawyerRegistrationForm()
    return render(request, "register_lawyer.html", {"form": form})


# -------- Public Questions --------

def public_questions(request):
    """
    Anyone: see answered questions.
    Logged-in customers: can submit up to 2 questions.
    Does NOT change your existing wording/layout.
    """
    answered = (
        PublicAnswer.objects
        .select_related("question", "lawyer")
        .order_by("-created_at")
    )

    question_form = None

    if request.user.is_authenticated and hasattr(request.user, "customer_profile"):
        if request.method == "POST":
            question_form = PublicQuestionForm(request.POST)
            if question_form.is_valid():
                existing_count = PublicQuestion.objects.filter(
                    customer=request.user
                ).count()
                if existing_count < 2:
                    q = question_form.save(commit=False)
                    q.customer = request.user
                    q.save()
                return redirect("public_questions")
        else:
            question_form = PublicQuestionForm()

    context = {
        "answers": answered,
        "question_form": question_form,
    }
    return render(request, "public_questions.html", context)


# -------- Lawyers List --------

def lawyers_list(request):
    """
    Public page: list approved lawyers.
    UI handled by your existing template; we just feed it data.
    """
    lawyers = (
        LawyerProfile.objects
        .select_related("user")
        .filter(is_approved=True)
        .order_by("user__last_name", "user__first_name")
    )
    return render(request, "lawyers_list.html", {"lawyers": lawyers})


# -------- My Questions (simple) --------

@login_required
def my_questions(request):
    """
    For customers: see their own public questions & answers.
    For lawyers: see questions they've answered.
    Keep it minimal; no layout changes.
    """
    if hasattr(request.user, "customer_profile"):
        questions = (
            PublicQuestion.objects
            .filter(customer=request.user)
            .select_related("public_answer")
            .order_by("-created_at")
        )
        context = {"mode": "customer", "questions": questions}
    elif hasattr(request.user, "lawyer_profile"):
        answers = (
            PublicAnswer.objects
            .filter(lawyer=request.user)
            .select_related("question")
            .order_by("-created_at")
        )
        context = {"mode": "lawyer", "answers": answers}
    else:
        context = {"mode": "none"}

    return render(request, "my_questions.html", context)


# -------- Answer Public Question (for lawyers) --------

@login_required
def answer_public_question(request, question_id):
    if not hasattr(request.user, "lawyer_profile"):
        return redirect("public_questions")

    question = get_object_or_404(PublicQuestion, pk=question_id)

    if hasattr(question, "public_answer"):
        return redirect("public_questions")

    if request.method == "POST":
        form = PublicAnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.lawyer = request.user
            answer.save()
            return redirect("public_questions")
    else:
        form = PublicAnswerForm()

    return render(
        request,
        "answer_public_question.html",
        {"question": question, "form": form},
    )
