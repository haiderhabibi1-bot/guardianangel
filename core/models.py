from django.db import models
from django.contrib.auth.models import User

# Lawyer profile model
class Lawyer(models.Model):
user = models.OneToOneField(User, on_delete=models.CASCADE)
speciality = models.CharField(max_length=100, blank=True)
years_experience = models.PositiveIntegerField(default=0)
law_school = models.CharField(max_length=100, blank=True)
bar_number = models.CharField(max_length=50, blank=True)
bar_certificate = models.FileField(upload_to='bar_certificates/', blank=True, null=True)
approved = models.BooleanField(default=False)

def __str__(self):
return self.user.username


# Client profile model
class Client(models.Model):
user = models.OneToOneField(User, on_delete=models.CASCADE)

def __str__(self):
return self.user.username


# General question model
class Question(models.Model):
client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
text = models.TextField()
created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
return f"Question #{self.id}"
