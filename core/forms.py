from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, BillingProfile, PublicQuestion, PublicAnswer


# =======================================================
# REGISTRATION FORMS
# =======================================================

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(
                user=user,
                role=Profile.ROLE_CUSTOMER,
                is_approved=True,
            )
            BillingProfile.objects.create(user=user)
        return user


class LawyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(label="Full Name", required=True)
    bar_number = forms.CharField(label="Bar Number", required=False)
    # NEW: upload field
    bar_certificate = forms.FileField(
        label="Bar Certificate (PDF or image)",
        required=False,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = Profile.objects.create(
                user=user,
                role=Profile.ROLE_LAWYER,
                is_approved=False,
                full_name=self.cleaned_data["full_name"],
                bar_number=self.cleaned_data.get("bar_number", ""),
            )
            # Save certificate file if provided
            cert = self.cleaned_data.get("bar_certificate")
            if cert:
                profile.bar_certificate = cert
                profile.save()

            BillingProfile.objects.create(user=user)
        return user


# =======================================================
# SETTINGS FORMS
# =======================================================

class CustomerSettingsForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    billing_method = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email
        self.fields["billing_method"].initial = getattr(
            getattr(user, "billing", None), "billing_method", ""
        )

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        self.user.save()

        billing, _ = BillingProfile.objects.get_or_create(user=self.user)
        billing.billing_method = self.cleaned_data["billing_method"]
        billing.save()


class LawyerSettingsForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    billing_method = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email
        self.fields["billing_method"].initial = getattr(
            getattr(user, "billing", None), "billing_method", ""
        )

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        self.user.save()

        billing, _ = BillingProfile.objects.get_or_create(user=self.user)
        billing.billing_method = self.cleaned_data["billing_method"]
        billing.save()


# =======================================================
# PUBLIC Q&A FORMS
# =======================================================

class PublicQuestionForm(forms.ModelForm):
    class Meta:
        model = PublicQuestion
        fields = ["question_text"]
        widgets = {
            "question_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ask your question anonymously...",
                    "class": "form-control",
                }
            )
        }


class PublicAnswerForm(forms.ModelForm):
    class Meta:
        model = PublicAnswer
        fields = ["answer_text"]
        widgets = {
            "answer_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Write a clear, helpful answer...",
                    "class": "form-control",
                }
            )
        }
