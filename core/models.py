from django.conf import settings
from django.db import models
from django.utils import timezone


class LawyerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255, blank=True)
    years_of_practice = models.PositiveIntegerField(default=0)
    bar_number = models.CharField(max_length=128, blank=True)
    bio = models.TextField(blank=True)
    fee_per_chat = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name or self.user.get_username()


class Profile(models.Model):
    """
    Simple wrapper so existing imports work.
    Flags whether a user is a customer or a lawyer.
    """
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("lawyer", "Lawyer"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="customer")
    lawyer_profile = models.OneToOneField(
        LawyerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="base_profile",
    )

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class BillingProfile(models.Model):
    """
    Minimal billing info to satisfy existing imports and templates.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"Billing for {self.user.username}"


class PublicQuestion(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ANSWERED = "answered"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ANSWERED, "Answered"),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    # used to enforce the "two free questions" rule
    is_free = models.BooleanField(default=True)

    def __str__(self):
        return f"Question #{self.id}"


class PublicAnswer(models.Model):
    question = models.OneToOneField(
        PublicQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
    )
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_answers",
    )
    answer_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Answer to #{self.question_id}"


class Chat(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chats_as_customer",
    )
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.CASCADE,
        related_name="chats_as_lawyer",
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat {self.id} {self.customer} ↔ {self.lawyer}"


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.content[:40]}"
