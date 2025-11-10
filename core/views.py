from django.shortcuts import render

def home(request):
    """
    Main 'Ask a Lawyer' page.
    Uses your existing home.html which should extend base.html.
    """
    return render(request, "home.html")


def public_questions(request):
    """
    Public questions listing (simple stub for now).
    """
    return render(request, "public_questions.html")


def lawyers_list(request):
    """
    List of approved / pending lawyers.
    Hook this up to your Lawyer model later.
    """
    return render(request, "lawyers_list.html")


def pricing(request):
    """
    Simple pricing/plan overview.
    """
    return render(request, "pricing.html")


def register_landing(request):
    """
    Landing page to choose between customer and lawyer registration.
    """
    return render(request, "register_landing.html")


def register_customer(request):
    """
    Customer registration page.
    Uses your existing register_customer.html.
    """
    return render(request, "register_customer.html")


def register_lawyer(request):
    """
    Lawyer registration page.
    Uses your existing register_lawyer.html.
    """
    return render(request, "register_lawyer.html")
