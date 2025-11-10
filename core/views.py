from django.shortcuts import render, redirect
from .models import PublicQuestion


def home(request):
    # Your main landing page
    return render(request, "home.html")


def public_questions(request):
    """
    Show a form to submit a question and list all submitted questions.
    """
    if request.method == "POST":
        text = (request.POST.get("question") or "").strip()
        if text:
            PublicQuestion.objects.create(text=text)
            return redirect("public_questions")

    questions = PublicQuestion.objects.all()
    return render(request, "public_questions.html", {"questions": questions})


def lawyers_list(request):
    return render(request, "lawyers_list.html")


def pricing(request):
    return render(request, "pricing.html")


def register_landing(request):
    return render(request, "register_landing.html")


def register_customer(request):
    return render(request, "register_customer.html")


def register_lawyer(request):
    return render(request, "register_lawyer.html")


def profile(request):
    return render(request, "profile.html")


def payment(request):
    return render(request, "payment.html")


def general_questions(request):
    return render(request, "general_questions.html")
