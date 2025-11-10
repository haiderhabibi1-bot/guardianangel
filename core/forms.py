from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, BillingProfile, PublicQuestion, PublicAnswer


# =======================================================
# REGISTRATION FORMS
# =======================================================

class CustomerRegistrationForm(UserCreationForm):
    """
    Customer registration form.
    Customers are auto-approved and immediately gain access to their profile.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Create associated Profile & BillingProfile
            Profile.objects.create(
                user=user,
                role=Profile.ROLE_CUSTOMER,
                is_approved=True,  # customers are instantly approved
            )
            BillingProfile.objects.create(user=user)
        return user


class LawyerRegistrationForm(UserCreationForm):
    """
    Lawyer registration form.
    Lawyers require manual approval before access to profile.
    """
    email = forms.EmailField(required=True)
    full_name = forms.CharField(label="Full Name", required=True)
    bar_number = forms.CharField(label="Bar Number", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Create Profile and BillingProfile (not approved yet)
            Profile.objects.create(
                user=user,
                role=Profile.ROLE_LAWYER,
                is_approved=False,
                full_name=self.cleaned_data["full_name"],
                bar_number=self.cleaned_data.get("bar_number", ""),
            )
            BillingProfile.objects.create(user=user)
        return user


# =======================================================
# SETTINGS FORMS
# =======================================================

class CustomerSettingsForm(forms.Form):
    """
    Customers can edit username, email, and billing method.
    They remain anonymous — no real names used.
    """
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    billing_method = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user
        # Initialize fields with current data
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email
        self.fields["billing_method"].initial = getattr(
            getattr(user, "billing", None), "billing_method", ""
        )

    def save(self):
        """Save updated customer settings."""
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        self.user.save()

        billing, _ = BillingProfile.objects.get_or_create(user=self.user)
        billing.billing_method = self.cleaned_data["billing_method"]
        billing.save()


class LawyerSettingsForm(forms.Form):
    """
    Lawyers can only edit username, email, and billing method.
    Their professional name and bar info are locked.
    """
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    billing_method = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user
        # Initialize fields with current data
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email
        self.fields["billing_method"].initial = getattr(
            getattr(user, "billing", None), "billing_method", ""
        )

    def save(self):
        """Save updated lawyer settings."""
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
    """
    Customers can post anonymous public questions.
    Displayed only once answered by a lawyer.
    """
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
    """
    Approved lawyers can answer questions.
    """
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
