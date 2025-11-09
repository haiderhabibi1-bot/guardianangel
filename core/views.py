from django.shortcuts import render

def home(request):
    # Uses core/templates/home.html which extends base.html (styled)
    return render(request, "home.html")

def login_view(request):
    # Simple placeholder login page for now
    return render(request, "login.html")

def register_customer(request):
    # Placeholder customer registration page
    return render(request, "register_customer.html")

def register_lawyer(request):
    # Placeholder lawyer registration page
    return render(request, "register_lawyer.html")

def general_questions(request):
    # Placeholder general Q&A page
    return render(request, "general_questions.html")

def lawyers_list(request):
    # Placeholder lawyers list page
    return render(request, "lawyers_list.html")
