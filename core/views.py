from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    PublicQuestionForm,
    PublicAnswerForm,
)
from .models import PublicQuestion, PublicAnswer, LawyerProfile


def home(request):
    return render(request, 'home.html')


def pricing(request):
    return render(request, 'pricing.html')


def lawyers_list(request):
    lawyers = LawyerProfile.objects.filter(approved=True)
    return render(request, 'lawyers_list.html', {'lawyers': lawyers})


def public_questions(request):
    """
    Show only answered public questions to everyone.
    No layout changes; template handles display.
    """
    answered = PublicQuestion.objects.filter(
        answers__isnull=False
    ).distinct().order_by('-created_at')
    return render(request, 'public_questions.html', {'questions': answered})


def register_customer(request):
    """
    Create customer account then log them in and send to My Questions.
    """
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your customer account has been created.")
            return redirect('my_questions')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register_customer.html', {'form': form})


def register_lawyer(request):
    """
    Create lawyer account in pending state; no style change.
    """
    if request.method == 'POST':
        form = LawyerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            lawyer_profile = form.save(commit=False)
            lawyer_profile.is_approved = False  # pending manual approval
            lawyer_profile.save()
            messages.success(
                request,
                "Your application has been submitted. You will be notified once approved."
            )
            return redirect('home')
    else:
        form = LawyerRegistrationForm()
    return render(request, 'register_lawyer.html', {'form': form})


@login_required
def my_questions(request):
    """
    Placeholder page for logged-in customers.
    Simple and cannot 500.
    """
    return render(request, 'my_questions.html')
