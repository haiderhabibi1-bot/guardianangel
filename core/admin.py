from django.contrib import admin
from .models import (
    CustomerProfile,
    LawyerProfile,
    BillingProfile,
    PublicQuestion,
    PublicAnswer,
)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bar_number", "years_of_experience", "approved")
    list_filter = ("approved",)
    search_fields = ("user__username", "user__email", "bar_number")


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(PublicQuestion)
class PublicQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "created_at", "is_answered")
    list_filter = ("is_answered",)
    search_fields = ("question_text", "customer__user__username")


@admin.register(PublicAnswer)
class PublicAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "lawyer", "question", "created_at")
    search_fields = ("question__question_text", "lawyer__user__username")
