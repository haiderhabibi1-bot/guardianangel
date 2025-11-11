from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    CustomerRegistrationForm,
    LawyerRegistrationForm,
)
from .models import PublicQuestion, LawyerProfile


def home(request):
    return render(request, 'home.html')


def pricing(request):
    return render(request, 'pricing.html')


def lawyers_list(request):
    lawyers = LawyerProfile.objects.filter(approved=True)
    return render(request, 'lawyers_list.html', {'lawyers': lawyers})


def public_questions(request):
    # show only answered questions publicly
    questions = PublicQuestion.objects.filter(
        answers__isnull=False
    ).distinct().order_by('-created_at')
    return render(request, 'public_questions.html', {'questions': questions})


def register_customer(request):
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
    if request.method == 'POST':
        form = LawyerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            # mark as pending; you already review/approve manually
            profile.is_approved = False
            profile.save()
            messages.success(
                request,
                "Your application has been submitted for approval."
            )
            return redirect('home')
    else:
        form = LawyerRegistrationForm()
    return render(request, 'register_lawyer.html', {'form': form})


@login_required
def my_questions(request):
    # Simple placeholder; no layout change.
    return render(request, 'my_questions.html')
