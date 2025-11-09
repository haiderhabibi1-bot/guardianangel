from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .models import LawyerProfile, GeneralQuestion


# ---------------------------
# LOGIN FORM
# ---------------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Username"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "Password"}
        ),
    )


# ---------------------------
# CUSTOMER REGISTRATION FORM
# ---------------------------
class CustomerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# ---------------------------
# LAWYER REGISTRATION FORM
# ---------------------------
class LawyerRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-input"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )

    class Meta:
        model = LawyerProfile
        fields = [
            "speciality",
            "years_experience",
            "law_school",
            "bar_number",
            "bar_certificate",
        ]
        widgets = {
            "speciality": forms.TextInput(attrs={"class": "form-input"}),
            "years_experience": forms.NumberInput(attrs={"class": "form-input"}),
            "law_school": forms.TextInput(attrs={"class": "form-input"}),
            "bar_number": forms.TextInput(attrs={"class": "form-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        # Create related User
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]

        user = User(username=username, email=email)
        user.set_password(password)
        if commit:
            user.save()

        # Create LawyerProfile
        lawyer = LawyerProfile(
            user=user,
            speciality=self.cleaned_data.get("speciality", ""),
            years_experience=self.cleaned_data.get("years_experience") or 0,
            law_school=self.cleaned_data.get("law_school", ""),
            bar_number=self.cleaned_data.get("bar_number", ""),
            bar_certificate=self.cleaned_data.get("bar_certificate"),
            approved=False,  # will be approved via admin
        )
        if commit:
            lawyer.save()

        return lawyer


# ---------------------------
# GENERAL QUESTION FORM
# ---------------------------
class GeneralQuestionForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestion
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 4,
                    "placeholder": "Ask your question here...",
                }
            )
        }
