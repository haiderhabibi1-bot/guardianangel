from django.shortcuts import render


def home(request):
    """
    Main 'Ask a Lawyer' page.
    Uses core/templates/home.html (which should extend base.html).
    """
    return render(request, "home.html")


def public_questions(request):
    """
    Public questions page (stub content for now).
    """
    return render(request, "public_questions.html")


def lawyers_list(request):
    """
    Approved / pending lawyers listing page.
    If you add a Lawyer model later, query it here and pass to the template.
    """
    return render(request, "lawyers_list.html")


def pricing(request):
    """
    Pricing information page.
    """
    return render(request, "pricing.html")


def register_landing(request):
    """
    Landing page letting users choose how they want to register.
    """
    return render(request, "register_landing.html")


def register_customer(request):
    """
    Customer registration page.
    Currently just renders your existing register_customer.html.
    """
    return render(request, "register_customer.html")


def register_lawyer(request):
    """
    Lawyer registration page.
    Currently just renders your existing register_lawyer.html.
    """
    return render(request, "register_lawyer.html")
