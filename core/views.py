from django.shortcuts import render

# ---------------------------
# CORE PAGES
# ---------------------------

def home(request):
    """
    Main landing page ('Ask a Lawyer' section)
    """
    return render(request, "home.html")


def public_questions(request):
    """
    Public Questions Page
    Displays sample or user-submitted public questions.
    """
    return render(request, "public_questions.html")


def lawyers_list(request):
    """
    Lists approved and pending lawyers.
    """
    return render(request, "lawyers_list.html")


def pricing(request):
    """
    Pricing page for question packages or subscriptions.
    """
    return render(request, "pricing.html")


# ---------------------------
# REGISTRATION & LOGIN
# ---------------------------

def register_landing(request):
    """
    Landing page to choose between customer and lawyer registration.
    """
    return render(request, "register_landing.html")


def register_customer(request):
    """
    Customer registration page.
    Allows users to create accounts to ask legal questions.
    """
    return render(request, "register_customer.html")


def register_lawyer(request):
    """
    Lawyer registration page.
    Allows lawyers to register and upload verification.
    """
    return render(request, "register_lawyer.html")


# ---------------------------
# OPTIONAL / FUTURE PAGES
# ---------------------------

def profile(request):
    """
    User profile page (optional placeholder).
    """
    return render(request, "profile.html")


def payment(request):
    """
    Payment page (optional placeholder for Stripe or PayPal integration).
    """
    return render(request, "payment.html")


def general_questions(request):
    """
    Optional section for general knowledge Q&A (FAQ-like content).
    """
    return render(request, "general_questions.html")
