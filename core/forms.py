from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Profile,
    BillingProfile,
    LawyerProfile,
    PublicQuestion,
    PublicAnswer,
    ChatMessage,
)


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LawyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255)
    specialty = forms.CharField(max_length=255, required=False)
    years_of_practice = forms.IntegerField(min_value=0, required=False)
    bar_number = forms.CharField(max_length=128, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class BillingProfileForm(forms.ModelForm):
    class Meta:
        model = BillingProfile
        fields = [
            "full_name",
            "address_line1",
            "address_line2",
            "city",
            "country",
        ]


class LawyerProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = LawyerProfile
        fields = [
            "full_name",
            "specialty",
            "years_of_practice",
            "bio",
            "fee_per_chat",
        ]


class PublicQuestionForm(forms.ModelForm):
    class Meta:
        model = PublicQuestion
        fields = ["question_text"]
        widgets = {
            "question_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ask your general legal question here",
                }
            )
        }


class PublicAnswerForm(forms.ModelForm):
    class Meta:
        model = PublicAnswer
        fields = ["answer_text"]
        widgets = {
            "answer_text": forms.Textarea(attrs={"rows": 4})
        }


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Type your message"}
            )
        }
