from django.contrib import admin
from .models import (
    PublicQuestion,
    LawyerProfile,
    CustomerProfile,
    LegalQuestion,
    Answer,
)


@admin.register(PublicQuestion)
class PublicQuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "created_at")
    search_fields = ("text",)

    def short_text(self, obj):
        return (obj.text[:75] + "...") if len(obj.text) > 75 else obj.text

    short_text.short_description = "Question"


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "speciality", "approved")
    list_filter = ("approved",)
    search_fields = ("user__username", "user__email", "speciality", "bar_number")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "joined_at")
    search_fields = ("user__username", "user__email")


@admin.register(LegalQuestion)
class LegalQuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "lawyer", "answered", "created_at")
    list_filter = ("answered", "created_at")
    search_fields = ("title", "description")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "lawyer", "created_at")
    search_fields = ("question__title", "text", "lawyer__user__username")
