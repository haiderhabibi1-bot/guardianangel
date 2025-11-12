from django.contrib import admin
from .models import (
    Profile,
    BillingProfile,
    LawyerProfile,
    PublicQuestion,
    PublicAnswer,
    Chat,
    ChatMessage,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_type")
    list_filter = ("user_type",)
    search_fields = ("user__username", "user__email")


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "country")
    search_fields = ("user__username", "full_name", "country")


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialty", "years_of_practice", "fee_per_chat", "is_approved")
    list_filter = ("is_approved", "specialty")
    search_fields = ("full_name", "user__username", "specialty")


@admin.register(PublicQuestion)
class PublicQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "created_at", "is_free")
    list_filter = ("status", "is_free")
    search_fields = ("question_text", "customer__username")


@admin.register(PublicAnswer)
class PublicAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "lawyer", "created_at")
    search_fields = ("answer_text", "lawyer__full_name")


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "lawyer", "created_at", "is_active")
    list_filter = ("is_active",)
    search_fields = ("customer__username", "lawyer__full_name")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "timestamp")
    search_fields = ("content", "sender__username")
    list_filter = ("timestamp",)
