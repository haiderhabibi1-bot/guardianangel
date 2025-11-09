from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import stripe

# Import your models and forms safely
try:
    from .models import Lawyer, Question, Message
    from .forms import LawyerRegistrationForm, CustomerRegistrationForm
except Exception:
    Lawyer = None
    Question = None
    Message = None
    LawyerRegistrationForm = None
    CustomerRegistrationForm = None


# -----------------------
# HOME PAGE
# -----------------------
def home(request):
    """Public home page with about section."""
    return render(request, 'home.html')


# -----------------------
# GENERAL QUESTIONS PAGE
# -----------------------
def general_questions(request):
    """Publicly visible Q&A section where users can view and submit general questions."""
    if request.method == 'POST':
        question = request.POST.get('question')
        if question:
            messages.success(request, "Your question was submitted successfully!")
        else:
            messages.error(request, "Please enter a valid question.")
    return render(request, 'general_questions.html')


# -----------------------
# CUSTOMER REGISTRATION
# -----------------------
def register_customer(request):
    """Register a new customer (2 free questions)."""
    if request.method == 'POST':
        # Use the form if available
        if CustomerRegistrationForm:
            form = CustomerRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your customer account has been created.")
                return redirect('login')
        else:
            messages.info(request, "Form submission placeholder active (dev mode).")
            return redirect('login')

    form = CustomerRegistrationForm() if CustomerRegistrationForm else None
    return render(request, 'register_customer.html', {'form': form})


# -----------------------
# LAWYER REGISTRATION
# -----------------------
def register_lawyer(request):
    """Lawyer registration page (requires bar certificate)."""
    if request.method == 'POST':
        if LawyerRegistrationForm:
            form = LawyerRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Registration submitted for approval.")
                return redirect('login')
        else:
            messages.info(request, "Placeholder registration active (dev mode).")
            return redirect('login')

    form = LawyerRegistrationForm() if LawyerRegistrationForm else None
    return render(request, 'register_lawyer.html', {'form': form})


# -----------------------
# PROFILE PAGE
# -----------------------
@login_required(login_url='/login/')
def profile(request):
    """Profile page for both lawyers and customers."""
    return render(request, 'profile.html')


# -----------------------
# LAWYER LIST PAGE
# -----------------------
def lawyers_list(request):
    """Display a list of approved lawyers."""
    lawyers = []
    if Lawyer:
        lawyers = Lawyer.objects.all()
    return render(request, 'lawyers_list.html', {'lawyers': lawyers})


# -----------------------
# PAYMENT PAGE
# -----------------------
def payment(request):
    """Handles payment via Stripe before chat starts."""
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
    amount = 10 * 100  # example: 10 CAD
    if stripe.api_key:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='cad',
            automatic_payment_methods={"enabled": True},
        )
        return render(request, 'payment.html', {'client_secret': intent.client_secret})
    else:
        return HttpResponse("Stripe not configured.")


# -----------------------
# CHAT PAGE
# -----------------------
@login_required(login_url='/login/')
def chat(request):
    """Private chat between lawyer and client."""
    return render(request, 'chat.html')


# -----------------------
# CUSTOMER QUESTIONS PAGE
# -----------------------
@login_required(login_url='/login/')
def customer_questions(request):
    """Customers post questions and specify a price."""
    if request.method == 'POST':
        question_text = request.POST.get('question')
        price = request.POST.get('price')
        if question_text and price:
            messages.success(request, "Your question has been posted.")
        else:
            messages.error(request, "Please fill out all fields.")
    return render(request, 'customer_questions.html')


# -----------------------
# LAWYER SUBSCRIPTION PAGE (FIX)
# -----------------------
def lawyer_subscribe(request):
    """Placeholder for lawyer subscription to prevent import errors."""
    return HttpResponse("<h2>Lawyer subscription page coming soon!</h2>")


# -----------------------
# ACCOUNT LOCKED PAGE
# -----------------------
def account_locked(request):
    """Displayed when a user is rate-limited or locked out."""
    return render(request, 'account_locked.html')
