from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import date


class Profile(models.Model):
    ROLE_CUSTOMER = "customer"
    ROLE_LAWYER = "lawyer"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_LAWYER, "Lawyer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Lawyer approval
    is_approved = models.BooleanField(default=False)

    # Lawyer details
    full_name = models.CharField(max_length=150, blank=True)
    bar_number = models.CharField(max_length=100, blank=True)
    bar_certificate = models.FileField(
        upload_to="bar_certificates/", blank=True, null=True
    )

    # Extra lawyer info
    specialty = models.CharField(max_length=255, blank=True)
    practice_start_year = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, max_length=1000)
    fee_per_chat = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_lawyer(self):
        return self.role == self.ROLE_LAWYER

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    @property
    def years_of_practice(self):
        if self.practice_start_year:
            return max(0, date.today().year - self.practice_start_year)
        return None

    @property
    def display_name(self):
        if self.is_lawyer:
            return self.full_name or self.user.username
        return self.user.username


class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="billing")
    billing_method = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Billing for {self.user.username}"


class PublicQuestion(models.Model):
    # Customer who asked (nullable so old data still works)
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Q#{self.id}"

    @property
    def is_answered(self):
        return hasattr(self, "answer")


class PublicAnswer(models.Model):
    question = models.OneToOneField(
        PublicQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
    )
    lawyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_answers",
    )
    answer_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Answer to Q#{self.question_id}"


class Chat(models.Model):
    """
    One chat between a customer and a lawyer, created after 'payment'.
    """

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_chats"
    )
    lawyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lawyer_chats"
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("customer", "lawyer")

    def __str__(self):
        return f"Chat {self.id} - {self.customer.username} x {self.lawyer.username}"


class ChatMessage(models.Model):
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Msg {self.id} in Chat {self.chat_id}"
