from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    ROLE_CUSTOMER = "customer"
    ROLE_LAWYER = "lawyer"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_LAWYER, "Lawyer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Lawyers must be approved by you before full access
    is_approved = models.BooleanField(default=False)

    # Optional fields for lawyers (not editable later except where allowed)
    full_name = models.CharField(max_length=150, blank=True)
    bar_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_lawyer(self):
        return self.role == self.ROLE_LAWYER

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER


class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="billing")
    # Placeholder: you can integrate Stripe/etc later
    billing_method = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Billing for {self.user.username}"


class PublicQuestion(models.Model):
    """
    Asked by a registered customer.
    Shown publicly ONLY once answered by an approved lawyer.
    Both appear anonymous.
    """
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    # Only questions with an answer (see PublicAnswer) will be shown on site.
    def __str__(self):
        return f"Q#{self.id} (by customer)"

    @property
    def is_answered(self):
        return hasattr(self, "answer")


class PublicAnswer(models.Model):
    """
    Answer provided by an approved lawyer.
    One answer per question for now (simple + controlled).
    """
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
