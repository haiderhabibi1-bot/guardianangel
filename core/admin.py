from django.contrib import admin
from .models import Profile, BillingProfile, PublicQuestion, PublicAnswer


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_approved", "full_name", "bar_number")
    list_filter = ("role", "is_approved")
    search_fields = ("user__username", "user__email", "full_name", "bar_number")


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "billing_method")
    search_fields = ("user__username", "user__email", "billing_method")


@admin.register(PublicQuestion)
class PublicQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "short_question", "customer", "created_at", "is_answered_flag")
    search_fields = ("question_text",)
    list_filter = ("created_at",)

    def short_question(self, obj):
        text = obj.question_text or ""
        return (text[:60] + "...") if len(text) > 60 else text
    short_question.short_description = "Question"

    def is_answered_flag(self, obj):
        return hasattr(obj, "answer")
    is_answered_flag.boolean = True
    is_answered_flag.short_description = "Answered"


@admin.register(PublicAnswer)
class PublicAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "lawyer", "created_at")
    search_fields = ("answer_text", "question__question_text", "lawyer__username")
