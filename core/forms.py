from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import GeneralQuestion, CustomerQuestion, Message
import bleach

# Sanitization rules to protect against XSS in questions or messages
ALLOWED_TAGS = ['b', 'i', 'strong', 'a', 'p', 'ul', 'li', 'br']
ALLOWED_ATTRS = {'a': ['href', 'rel', 'target']}


def sanitize(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)


class CustomerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LawyerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    specialty = forms.CharField(max_length=255)
    years_practicing = forms.IntegerField(min_value=0)
    graduation_institution = forms.CharField(max_length=255)
    question_price = forms.DecimalField(min_value=10, max_value=30, decimal_places=2)
    bar_certificate = forms.FileField()

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'specialty', 'years_practicing', 'graduation_institution',
            'question_price', 'bar_certificate'
        ]


class GeneralQuestionForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestion
        fields = ['text']

    def clean_text(self):
        return sanitize(self.cleaned_data['text'])


class GeneralQuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestion
        fields = ['answer_text']

    def clean_answer_text(self):
        return sanitize(self.cleaned_data['answer_text'])


class CustomerQuestionForm(forms.ModelForm):
    class Meta:
        model = CustomerQuestion
        fields = ['title', 'text', 'offered_price']

    def clean_text(self):
        return sanitize(self.cleaned_data['text'])


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']

    def clean_text(self):
        return sanitize(self.cleaned_data['text'])
