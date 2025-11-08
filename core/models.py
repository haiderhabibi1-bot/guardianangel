from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_upload_file


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )

    def __str__(self):
        return f"Customer: {self.user.username}"


class LawyerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='lawyer_profile'
    )
    specialty = models.CharField(max_length=255)
    years_practicing = models.PositiveIntegerField(default=0)
    graduation_institution = models.CharField(max_length=255)
    question_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(10), MaxValueValidator(30)]
    )
    bar_certificate = models.FileField(
        upload_to='bar_certificates/',
        validators=[validate_upload_file],
    )
    is_approved = models.BooleanField(default=False)
    subscription_active = models.BooleanField(default=False)

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"Lawyer: {name}"


class GeneralQuestion(models.Model):
    """
    Public, anonymous Q&A.
    - Customer can ask (up to 2 free).
    - If answered by a lawyer, answer is public.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='general_questions'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_answered = models.BooleanField(default=False)
    answer_text = models.TextField(blank=True)
    answered_by = models.ForeignKey(
        LawyerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='general_answers'
    )

    def display_name(self):
        # Always shown as anonymous on site
        return "Anonymous"

    def __str__(self):
        return f"General Q #{self.id} ({'answered' if self.is_answered else 'open'})"


class CustomerQuestion(models.Model):
    """
    Customer posts a question with a price offer (10–30 CAD).
    Lawyers can pick it up and start a paid chat.
    """
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_questions'
    )
    title = models.CharField(max_length=255)
    text = models.TextField()
    offered_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(10), MaxValueValidator(30)]
    )
    is_open = models.BooleanField(default=True)
    chosen_lawyer = models.ForeignKey(
        'LawyerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taken_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer Q #{self.id} by {self.customer.username}"


class ChatSession(models.Model):
    """
    Represents a paid (or to-be-paid) chat between a customer and a lawyer.
    Each “Message” belongs to one ChatSession.
    """
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )

    related_general_question = models.ForeignKey(
        GeneralQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )
    related_customer_question = models.ForeignKey(
        CustomerQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Payment flags
    requires_payment = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Chat {self.id}: {self.customer.username} ↔ {self.lawyer.user.username}"


class Message(models.Model):
    """
    Individual message inside a chat between customer and lawyer.
    """
    chat = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg {self.id} in Chat {self.chat.id} by {self.sender.username}"


class Payment(models.Model):
    """
    Stores both:
    - per-chat payments
    - lawyer subscription payments
    """
    PAYMENT_TYPES = (
        ('chat', 'Chat'),
        ('subscription', 'Subscription'),
    )

    chat = models.OneToOneField(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.CASCADE,
        related_name='subscription_payments',
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=7, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)

    stripe_session_id = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.payment_type == 'chat' and self.chat:
            return f"Chat Payment #{self.id} for Chat {self.chat.id} - {self.amount} CAD"
        if self.payment_type == 'subscription' and self.lawyer:
            return f"Subscription Payment #{self.id} for {self.lawyer.user.username} - {self.amount} CAD"
        return f"Payment #{self.id} - {self.amount} CAD"
