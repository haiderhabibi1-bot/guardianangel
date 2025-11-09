from django.db import models
from django.contrib.auth.models import User
from .validators import validate_upload_file


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    free_questions_left = models.PositiveIntegerField(default=2)

    def __str__(self):
        return f"CustomerProfile({self.user.username})"


class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=120, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    law_school = models.CharField(max_length=200, blank=True)
    bar_number = models.CharField(max_length=100, blank=True)
    bar_certificate = models.FileField(
        upload_to="bar_certificates/",
        validators=[validate_upload_file],
        blank=True,
        null=True,
    )
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"LawyerProfile({self.user.username})"


class GeneralQuestion(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"Q#{self.id} by {self.user or 'anonymous'}"
