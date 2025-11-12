from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")

    def __str__(self):
        return f"Customer: {self.user.username}"


class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lawyer_profile")
    bar_certificate = models.FileField(upload_to="bar_certificates/", blank=True, null=True)
    is_approved = models.BooleanField(default=True)  # keep True so your list works immediately

    def __str__(self):
        return f"Lawyer: {self.user.get_full_name() or self.user.username}"


class PublicQuestion(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question #{self.id}"


class PublicAnswer(models.Model):
    question = models.OneToOneField(
        PublicQuestion,
        on_delete=models.CASCADE,
        related_name="public_answer",
    )
    lawyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_answers",
    )
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to Q#{self.question_id}"
