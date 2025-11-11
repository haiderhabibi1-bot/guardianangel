from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Profile,
    BillingProfile,
    PublicQuestion,
    PublicAnswer,
    ChatMessage,
)


# =========================
# REGISTRATION FORMS
# =========================

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
    bar_certificate = forms.FileField(
        label="Bar Certificate (PDF or image)",
        required=False,
    )
    specialty = forms.CharField(label="Specialty", required=False)
    practice_start_year = forms.IntegerField(
        label="Year you started practicing (YYYY)",
        required=False,
        min_value=1950,
        max_value=2100,
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
                specialty=self.cleaned_data.get("specialty", ""),
                practice_start_year=self.cleaned_data.get("practice_start_year") or None,
            )
            cert = self.cleaned_data.get("bar_certificate")
            if cert:
                profile.bar_certificate = cert
                profile.save()

            BillingProfile.objects.create(user=user)
        return user


# =========================
# SETTINGS FORMS
# =========================

class CustomerSettingsForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    billing_method = forms.CharField(max_length=255, required=False)
    password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to keep current password.",
    )

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

        if self.cleaned_data.get("password"):
            self.user.set_password(self.cleaned_data["password"])
            self.user.save()

        billing, _ = BillingProfile.objects.get_or_create(user=self.user)
        billing.billing_method = self.cleaned_data["billing_method"]
        billing.save()


class LawyerSettingsForm(forms.Form):
    full_name = forms.CharField(max_length=150, required=True)
    specialty = forms.CharField(max_length=255, required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=1000,
        required=False,
    )
    fee_per_chat = forms.DecimalField(
        max_digits=8, decimal_places=2, required=False, min_value=0
    )
    email = forms.EmailField()
    billing_method = forms.CharField(max_length=255, required=False)
    password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to keep current password.",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user
        profile = user.profile

        self.fields["full_name"].initial = profile.full_name
        self.fields["specialty"].initial = profile.specialty
        self.fields["bio"].initial = profile.bio
        self.fields["fee_per_chat"].initial = profile.fee_per_chat
        self.fields["email"].initial = user.email
        self.fields["billing_method"].initial = getattr(
            getattr(user, "billing", None), "billing_method", ""
        )

    def save(self):
        profile = self.user.profile

        profile.full_name = self.cleaned_data["full_name"]
        profile.specialty = self.cleaned_data.get("specialty", "")
        profile.bio = self.cleaned_data.get("bio", "")
        profile.fee_per_chat = self.cleaned_data.get("fee_per_chat")
        profile.save()

        self.user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("password"):
            self.user.set_password(self.cleaned_data["password"])
        self.user.save()

        billing, _ = BillingProfile.objects.get_or_create(user=self.user)
        billing.billing_method = self.cleaned_data["billing_method"]
        billing.save()


# =========================
# PUBLIC Q&A FORMS
# =========================

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


# =========================
# CHAT FORMS
# =========================

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Type your message...",
                }
            )
        }
