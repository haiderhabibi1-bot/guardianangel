from django.contrib import admin
from .models import (
    CustomerProfile,
    LawyerProfile,
    PublicQuestion,
    PublicAnswer,
)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_approved")


@admin.register(PublicQuestion)
class PublicQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "created_at")
    search_fields = ("question_text",)


@admin.register(PublicAnswer)
class PublicAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "lawyer", "created_at")
    search_fields = ("answer_text",)
