from django.db import models
from django.contrib.auth.models import User


# -----------------------------------
# PUBLIC QUESTIONS
# -----------------------------------
class PublicQuestion(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text[:80]


# -----------------------------------
# LAWYER PROFILE
# -----------------------------------
class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=255, blank=True, null=True)
    years_of_practice = models.PositiveIntegerField(blank=True, null=True)
    law_school = models.CharField(max_length=255, blank=True, null=True)
    bar_number = models.CharField(max_length=100, blank=True, null=True)
    bar_certificate = models.FileField(upload_to="bar_certificates/", blank=True, null=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Lawyer: {self.user.username}"


# -----------------------------------
# CUSTOMER PROFILE
# -----------------------------------
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.username}"


# -----------------------------------
# LEGAL QUESTIONS (PRIVATE / DIRECT)
# -----------------------------------
class LegalQuestion(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'Answered' if self.answered else 'Pending'})"


# -----------------------------------
# ANSWERS
# -----------------------------------
class Answer(models.Model):
    question = models.ForeignKey(LegalQuestion, on_delete=models.CASCADE)
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.lawyer.user.username} to {self.question.title}"
