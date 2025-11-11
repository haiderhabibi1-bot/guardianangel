from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    """
    Basic customer profile used for:
    - linking a Django user to customer data
    - storing billing info (you can extend later)
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_profile"
        # username is what you show in the navbar for customers
    )
    billing_name = models.CharField(max_length=255, blank=True)
    billing_address = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


class LawyerProfile(models.Model):
    """
    Lawyer profile EXPECTED by your existing views/templates:
    - used on Lawyers List
    - used when answering public questions
    - bar_certificate upload already wired in your forms/templates
    DO NOT change field names here without also changing migrations/views.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="lawyer_profile"
    )

    # Display name on navbar & lawyers list
    full_name = models.CharField(max_length=255, blank=True)

    # Public info for Lawyers List
    specialty = models.CharField(max_length=255, blank=True)
    years_of_practice = models.PositiveIntegerField(default=0)
    bio = models.TextField(max_length=1000, blank=True)

    # Pricing for chats (shown on Lawyers List)
    fee_per_chat = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )

    # File upload field used on “Register as Lawyer”
    bar_certificate = models.FileField(
        upload_to="bar_certificates/", blank=True, null=True
    )

    # Only approved lawyers should appear as “approved” (list view can filter)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        # Use name if available, otherwise username
        return self.full_name or self.user.get_full_name() or self.user.username


class PublicQuestion(models.Model):
    """
    Public legal question asked by a customer.
    - Only ANSWERED questions are shown to everyone on /public-questions/.
    - The same structure you were already using.
    """
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="public_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # You mentioned “two free questions”; this flag lets you implement that
    is_free = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text[:80]


class PublicAnswer(models.Model):
    """
    Lawyer’s answer to a public question.
    - Once this exists, the Q&A is visible on the Public Questions page.
    """
    question = models.OneToOneField(
        PublicQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
    )
    lawyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="public_answers",
    )
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to question #{self.question_id}"
