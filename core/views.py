from decimal import Decimal
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

import stripe

from .models import (
    CustomerProfile,
    LawyerProfile,
    GeneralQuestion,
    CustomerQuestion,
    ChatSession,
    Message,
    Payment
)
from .forms import (
    CustomerRegisterForm,
    LawyerRegisterForm,
    GeneralQuestionForm,
    CustomerQuestionForm,
    MessageForm,
    GeneralQuestionAnswerForm
)

stripe.api_key = settings.STRIPE_SECRET_KEY


def is_lawyer(user):
    return hasattr(user, 'lawyer_profile') and user.lawyer_profile.is_approved


def is_customer(user):
    return hasattr(user, 'customer_profile')


def can_start_new_chat(customer, lawyer=None, minutes=3):
    """
    Simple anti-spam guard:
    Prevents opening many new chats with the same lawyer in a short period.
    """
    since = timezone.now() - timedelta(minutes=minutes)
    qs = ChatSession.objects.filter(customer=customer, created_at__gte=since)
    if lawyer:
        qs = qs.filter(lawyer=lawyer)
    return not qs.exists()


def home(request):
    return render(request, 'home.html')


def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Customer account created.")
            return redirect('home')
    else:
        form = CustomerRegisterForm()
    return render(request, 'register_customer.html', {'form': form})


def register_lawyer(request):
    if request.method == 'POST':
        form = LawyerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            LawyerProfile.objects.create(
                user=user,
                specialty=form.cleaned_data['specialty'],
                years_practicing=form.cleaned_data['years_practicing'],
                graduation_institution=form.cleaned_data['graduation_institution'],
                question_price=form.cleaned_data['question_price'],
                bar_certificate=form.cleaned_data['bar_certificate'],
                is_approved=False,
                subscription_active=False
            )
            # Notify admin (for now goes to console or DEFAULT_FROM_EMAIL)
            send_mail(
                "New lawyer registration",
                f"Lawyer {user.username} has registered and awaits approval.",
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.info(request, "Lawyer account created. Await approval from admin.")
            login(request, user)
            return redirect('home')
    else:
        form = LawyerRegisterForm()
    return render(request, 'register_lawyer.html', {'form': form})


@login_required
def profile(request):
    ctx = {
        'is_lawyer': is_lawyer(request.user),
        'is_customer': is_customer(request.user),
    }
    if is_lawyer(request.user):
        ctx['lawyer'] = request.user.lawyer_profile
    if is_customer(request.user):
        ctx['customer'] = request.user.customer_profile
    return render(request, 'profile.html', ctx)


@login_required
def lawyer_subscribe(request):
    """
    Lawyer subscription: 15 CAD/month.
    If Stripe keys not set, simulates success (dev mode).
    """
    if not hasattr(request.user, 'lawyer_profile'):
        messages.error(request, "Only lawyers can subscribe.")
        return redirect('home')

    lawyer = request.user.lawyer_profile

    if request.method == 'POST':
        # Dev fallback (no Stripe configured)
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLIC_KEY:
            Payment.objects.create(
                lawyer=lawyer,
                amount=Decimal('15.00'),
                payment_type='subscription',
                success=True,
            )
            lawyer.subscription_active = True
            lawyer.save()
            messages.success(request, "Subscription activated (development mode).")
            return redirect('profile')

        domain = request.build_absolute_uri('/')[:-1]
        amount_cents = 1500  # 15 CAD

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'cad',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': 'Guardian Angel Lawyer Monthly Access',
                    },
                },
                'quantity': 1,
            }],
            success_url=f"{domain}/profile?sub=success",
            cancel_url=f"{domain}/profile?sub=cancel",
            metadata={
                'payment_type': 'subscription',
                'lawyer_id': str(lawyer.id),
            }
        )

        Payment.objects.create(
            lawyer=lawyer,
            amount=Decimal('15.00'),
            payment_type='subscription',
            stripe_session_id=checkout_session.id,
            success=False,
        )

        return redirect(checkout_session.url, code=303)

    return render(request, 'lawyer_subscribe.html', {'lawyer': lawyer})


def lawyer_list(request):
    lawyers = LawyerProfile.objects.filter(is_approved=True, subscription_active=True)
    return render(request, 'lawyers_list.html', {'lawyers': lawyers})


def lawyer_detail(request, pk):
    lawyer = get_object_or_404(LawyerProfile, pk=pk, is_approved=True, subscription_active=True)
    can_message = request.user.is_authenticated and is_customer(request.user)
    return render(request, 'lawyer_detail.html', {
        'lawyer': lawyer,
        'can_message': can_message,
    })


@login_required
def start_chat_with_lawyer(request, pk):
    """
    Customer starts a new paid chat with a lawyer.
    Each click = a new chat (if not rate-limited).
    """
    if not is_customer(request.user):
        messages.error(request, "Only customers can start chats with lawyers.")
        return redirect('home')

    lawyer = get_object_or_404(LawyerProfile, pk=pk, is_approved=True, subscription_active=True)

    if not can_start_new_chat(request.user, lawyer):
        messages.error(
            request,
            "You recently opened a chat with this lawyer. Use that chat or wait a few minutes."
        )
        return redirect('lawyer_detail', pk=lawyer.id)

    chat = ChatSession.objects.create(
        customer=request.user,
        lawyer=lawyer,
        requires_payment=True,
        is_paid=False
    )
    return redirect('payment_view', chat_id=chat.id)


@login_required
def general_questions(request):
    """
    General Q&A:
    - Customers: up to 2 free anonymous questions, answers are public.
    - Lawyers: see pending unanswered questions & can answer them.
    """
    answered = GeneralQuestion.objects.filter(is_answered=True).order_by('-created_at')

    user_free_count = 0
    can_ask = False
    form = None

    # Customer: ask up to 2 questions
    if is_customer(request.user):
        user_free_count = GeneralQuestion.objects.filter(author=request.user).count()
        can_ask = user_free_count < 2

        if request.method == 'POST' and request.POST.get('action') == 'ask' and can_ask:
            form = GeneralQuestionForm(request.POST)
            if form.is_valid():
                q = form.save(commit=False)
                q.author = request.user
                q.save()
                send_mail(
                    "New general question posted",
                    f"Customer {request.user.username} posted a general question.",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
                messages.success(
                    request,
                    "Your question has been submitted. If answered, it will appear here anonymously."
                )
                return redirect('general_questions')
        else:
            form = GeneralQuestionForm()

    # Lawyer: answer pending questions
    if is_lawyer(request.user) and request.method == 'POST' and request.POST.get('action') == 'answer':
        qid = request.POST.get('question_id')
        question = get_object_or_404(GeneralQuestion, pk=qid, is_answered=False)
        answer_form = GeneralQuestionAnswerForm(request.POST, instance=question)
        if answer_form.is_valid():
            answered_q = answer_form.save(commit=False)
            answered_q.is_answered = True
            answered_q.answered_by = request.user.lawyer_profile
            answered_q.save()
            messages.success(request, "You answered this general question.")
            return redirect('general_questions')

    pending_questions = []
    pending_forms = {}
    if is_lawyer(request.user):
        pending_questions = GeneralQuestion.objects.filter(is_answered=False).order_by('-created_at')
        pending_forms = {q.id: GeneralQuestionAnswerForm(instance=q) for q in pending_questions}

    return render(request, 'general_questions.html', {
        'questions': answered,
        'can_ask': can_ask,
        'form': form,
        'user_free_count': user_free_count,
        'pending_questions': pending_questions,
        'pending_forms': pending_forms,
        'is_lawyer_flag': is_lawyer(request.user),
    })


@login_required
def customer_questions_list(request):
    """
    Shared /questions page:
    - Customers: see and create their own 'offer-price' questions.
    - Lawyers: see all open customer questions to pick from.
    """
    if is_lawyer(request.user):
        questions = CustomerQuestion.objects.filter(is_open=True).order_by('-created_at')
        return render(request, 'customer_questions.html', {
            'questions': questions,
            'is_lawyer': True,
            'is_customer': False,
        })

    elif is_customer(request.user):
        questions = CustomerQuestion.objects.filter(customer=request.user).order_by('-created_at')
        form = CustomerQuestionForm()
        return render(request, 'customer_questions.html', {
            'questions': questions,
            'form': form,
            'is_lawyer': False,
            'is_customer': True,
        })

    messages.error(request, "You need an account to view questions.")
    return redirect('home')


@login_required
def create_customer_question(request):
    """
    Customer posts a question with an offered price (10–30 CAD).
    Lawyers can later choose to answer and start a paid chat.
    """
    if not is_customer(request.user):
        messages.error(request, "Only customers can post questions.")
        return redirect('home')

    if request.method == 'POST':
        form = CustomerQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.customer = request.user
            q.save()
            send_mail(
                "New paid question posted",
                f"Customer {request.user.username} posted a paid question: {q.title}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, "Your question has been posted. Lawyers may contact you.")
    return redirect('customer_questions_list')


@login_required
def lawyer_answer_customer_question(request, pk):
    """
    Lawyer clicks "Answer" on an open customer question:
    - Reserves that question.
    - Creates a new chat that requires payment by the customer.
    """
    if not is_lawyer(request.user):
        messages.error(request, "Only approved lawyers can answer questions.")
        return redirect('home')

    question = get_object_or_404(CustomerQuestion, pk=pk, is_open=True)
    lawyer = request.user.lawyer_profile

    if request.method == 'POST':
        chat = ChatSession.objects.create(
            customer=question.customer,
            lawyer=lawyer,
            related_customer_question=question,
            requires_payment=True,
            is_paid=False
        )
        question.is_open = False
        question.chosen_lawyer = lawyer
        question.save()

        send_mail(
            "A lawyer accepted your question",
            f"Lawyer {lawyer.user.username} has accepted your question '{question.title}'. "
            f"Please complete payment to start chatting.",
            settings.DEFAULT_FROM_EMAIL,
            [question.customer.email],
            fail_silently=True,
        )

        return redirect('payment_view', chat_id=chat.id)

    return redirect('customer_questions_list')


@login_required
def payment_view(request, chat_id):
    """
    Handles payment for a chat:
    - Uses lawyer's price or customer's offered price.
    - Adds 2 CAD platform fee.
    - Adds tax (configurable).
    - If Stripe not configured, simulates success for testing.
    """
    chat = get_object_or_404(ChatSession, pk=chat_id)

    # Only participants can see
    if request.user != chat.customer and request.user != chat.lawyer.user:
        return HttpResponseForbidden("Not allowed.")

    if chat.is_paid:
        return redirect('chat_view', chat_id=chat.id)

    # Determine base amount
    if chat.related_customer_question:
        base = chat.related_customer_question.offered_price
    else:
        base = chat.lawyer.question_price

    base = Decimal(base)
    platform_fee = settings.PLATFORM_FEE
    subtotal = (base + platform_fee).quantize(Decimal('0.01'))
    tax_amount = (subtotal * settings.TAX_RATE).quantize(Decimal('0.01'))
    total = (subtotal + tax_amount).quantize(Decimal('0.01'))
    amount_cents = int(total * 100)

    if request.method == 'POST':
        # Dev fallback: auto-pay if no Stripe keys
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLIC_KEY:
            Payment.objects.update_or_create(
                chat=chat,
                defaults={
                    'amount': total,
                    'payment_type': 'chat',
                    'success': True,
                }
            )
            chat.is_paid = True
            chat.save()
            messages.success(request, "Payment confirmed (development mode). Chat unlocked.")
            return redirect('chat_view', chat_id=chat.id)

        # Real Stripe Checkout
        domain = request.build_absolute_uri('/')[:-1]
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'cad',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': f'Guardian Angel Legal Question with {chat.lawyer.user.username}',
                    },
                },
                'quantity': 1,
            }],
            success_url=f"{domain}/chat/{chat.id}",
            cancel_url=f"{domain}/payment/{chat.id}",
            metadata={
                'payment_type': 'chat',
                'chat_id': str(chat.id),
            }
        )

        Payment.objects.update_or_create(
            chat=chat,
            defaults={
                'amount': total,
                'payment_type': 'chat',
                'stripe_session_id': checkout_session.id,
                'success': False,
            }
        )

        return redirect(checkout_session.url, code=303)

    return render(request, 'payment.html', {
        'chat': chat,
        'base': base,
        'platform_fee': platform_fee,
        'tax_amount': tax_amount,
        'amount': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def chat_view(request, chat_id):
    """
    Chat interface between customer and lawyer.
    Only available after payment (if required).
    """
    chat = get_object_or_404(ChatSession, pk=chat_id)

    if request.user != chat.customer and request.user != chat.lawyer.user:
        return HttpResponseForbidden("Not allowed.")

    if chat.requires_payment and not chat.is_paid:
        messages.info(request, "Please complete payment before chatting.")
        return redirect('payment_view', chat_id=chat.id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.chat = chat
            msg.sender = request.user
            msg.save()
            return redirect('chat_view', chat_id=chat.id)
    else:
        form = MessageForm()

    messages_qs = chat.messages.all()
    return render(request, 'chat.html', {
        'chat': chat,
        'messages': messages_qs,
        'form': form,
    })


@csrf_exempt
def stripe_webhook(request):
    """
    Webhook endpoint for Stripe to confirm real payments.
    In dev (no STRIPE_WEBHOOK_SECRET), it just returns 200.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    # If no secret set, we don't process (dev mode).
    if not endpoint_secret:
        return HttpResponse(status=200)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        metadata = session.get('metadata', {}) or {}
        payment_type = metadata.get('payment_type')

        try:
            payment = Payment.objects.get(stripe_session_id=session_id)
        except Payment.DoesNotExist:
            payment = None

        if payment:
            payment.success = True
            payment.save()

            if payment_type == 'chat' and payment.chat:
                chat = payment.chat
                chat.is_paid = True
                chat.save()
                send_mail(
                    "Chat payment confirmed",
                    f"Your chat #{chat.id} is now unlocked.",
                    settings.DEFAULT_FROM_EMAIL,
                    [chat.customer.email, chat.lawyer.user.email],
                    fail_silently=True,
                )

            if payment_type == 'subscription' and payment.lawyer:
                lawyer = payment.lawyer
                lawyer.subscription_active = True
                lawyer.save()
                send_mail(
                    "Subscription activated",
                    "Your Guardian Angel lawyer subscription is now active.",
                    settings.DEFAULT_FROM_EMAIL,
                    [lawyer.user.email],
                    fail_silently=True,
                )

    return HttpResponse(status=200)
