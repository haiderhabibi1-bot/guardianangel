from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from .models import Lawyer, Question, Chat, Message
from .forms import CustomerRegistrationForm, LawyerRegistrationForm, QuestionForm
import stripe

# ===============================
# HOME PAGE (inline HTML + style)
# ===============================

def home(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Guardian Angel</title>
        <style>
            body {
                margin: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: radial-gradient(circle at top, #e6f3ff 0%, #c7ddff 40%, #eef4ff 100%);
                color: #404040;
            }
            header {
                background: #dfeeff;
                padding: 14px 32px;
                border-bottom: 2px solid #4a90e2;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                text-align: center;
            }
            h1 {
                color: #333;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .container {
                max-width: 1080px;
                margin: 40px auto 32px;
                padding: 24px 26px 32px;
                background: rgba(255,255,255,0.98);
                border-radius: 18px;
                box-shadow: 0 14px 40px rgba(0,0,0,0.06);
            }
            h2 {
                color: #555;
                text-shadow: 0 1px 1px #fff, 0 -1px 1px #999;
                margin-top: 0;
            }
            p {
                line-height: 1.6;
                font-size: 1rem;
            }
            footer {
                text-align: center;
                padding: 14px;
                font-size: 0.8rem;
                color: #7a7a7a;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Guardian Angel</h1>
        </header>
        <div class="container">
            <h2>About Us</h2>
            <p>
                At Guardian Angel, we know that sometimes it feels like you have to sign with the devil
                just to make it through. We understand that mental illness can cloud your clarity of mind,
                and that it can feel like you're walking through a storm in a world where phones throw off
                your natural compass. We've been through all the trials, we've seen all the possibilities,
                and we're here so you don't have to go through it all—without risking a human’s mental health
                to do it. We have AI to take care of that. At Guardian Angel, we never lose control, and we
                keep things steady at home. Help us help you. Accept this helping hand—though it may be artificial,
                its impact will be real.
            </p>
            <br><br>
            <h2>À propos de nous</h2>
            <p>
                On le sait chez Guardian Angel que parfois vous sentez qu’il faut signer chez le diable pour
                s’en sortir, on le sait que la maladie mentale vous enlève votre clarté d’esprit et que vous avez
                l’impression de marcher et vous diriger dans une tempête dans un monde où les téléphones
                dérèglent votre boussole naturelle. On est passé par toutes les épreuves, on a vu toutes les
                possibilités et on est là pour que vous n’ayez pas à le faire, sans risquer la santé mentale d’un
                humain pour le faire. On a des AI pour le faire. Chez Guardian Angel, on ne perd jamais les pédales
                et on garde le contrôle à la maison. Aidez-nous à vous aider, acceptez ce coup de main, bien qu’il
                soit artificiel, il sera d’un impact réel.
            </p>
        </div>
        <footer>
            &copy; Guardian Angel. All rights reserved.
        </footer>
    </body>
    </html>
    """
    return HttpResponse(html)

# ===============================
# USER REGISTRATION & LOGIN
# ===============================

def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register_customer.html", {"form": form})

def register_lawyer(request):
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            lawyer = form.save(commit=False)
            lawyer.is_approved = False
            lawyer.save()
            messages.info(request, "Your registration is pending approval.")
            return redirect("login")
    else:
        form = LawyerRegistrationForm()
    return render(request, "register_lawyer.html", {"form": form})

# ===============================
# PROFILE PAGE
# ===============================

@login_required
def profile(request):
    user = request.user
    try:
        lawyer = user.lawyer
    except:
        lawyer = None
    return render(request, "profile.html", {"user": user, "lawyer": lawyer})

# ===============================
# LAWYER LISTING & DETAIL
# ===============================

def lawyers_list(request):
    lawyers = Lawyer.objects.filter(is_approved=True)
    return render(request, "lawyers_list.html", {"lawyers": lawyers})

def lawyer_detail(request, lawyer_id):
    lawyer = get_object_or_404(Lawyer, id=lawyer_id, is_approved=True)
    return render(request, "lawyer_detail.html", {"lawyer": lawyer})

# ===============================
# GENERAL QUESTIONS
# ===============================

def general_questions(request):
    questions = Question.objects.filter(is_public=True)
    return render(request, "general_questions.html", {"questions": questions})

# ===============================
# CUSTOMER QUESTIONS
# ===============================

@login_required
def customer_questions(request):
    if not hasattr(request.user, "customer"):
        messages.error(request, "Only customers can post questions.")
        return redirect("home")

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.customer = request.user.customer
            question.save()
            messages.success(request, "Your question was posted successfully.")
            return redirect("customer_questions")
    else:
        form = QuestionForm()

    questions = Question.objects.filter(customer=request.user.customer)
    return render(request, "customer_questions.html", {"form": form, "questions": questions})

# ===============================
# CHAT PAGE
# ===============================

@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages_list = Message.objects.filter(chat=chat).order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)
            return redirect("chat_view", chat_id=chat.id)

    return render(request, "chat.html", {"chat": chat, "messages": messages_list})

# ===============================
# PAYMENT (STRIPE)
# ===============================

@login_required
def payment(request, lawyer_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    lawyer = get_object_or_404(Lawyer, id=lawyer_id)
    amount = int(lawyer.price * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "cad",
                "product_data": {"name": f"Consultation with {lawyer.user.get_full_name()}"},
                "unit_amount": amount,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://guardianangelconsulting.ca/profile/",
        cancel_url="https://guardianangelconsulting.ca/",
    )
    return redirect(session.url, code=303)
