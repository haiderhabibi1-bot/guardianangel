from django.contrib import admin
from .models import (
    CustomerProfile,
    LawyerProfile,
    GeneralQuestion,
    CustomerQuestion,
    ChatSession,
    Payment
)

@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'is_approved', 'subscription_active')
    list_filter = ('is_approved', 'subscription_active')
    search_fields = ('user__username', 'user__email', 'specialty')
    readonly_fields = ('bar_certificate',)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(GeneralQuestion)
class GeneralQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_answered', 'answered_by', 'created_at')
    list_filter = ('is_answered',)
    search_fields = ('text',)

@admin.register(CustomerQuestion)
class CustomerQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'offered_price', 'is_open', 'chosen_lawyer', 'created_at')
    list_filter = ('is_open',)
    search_fields = ('title', 'text')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'lawyer', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'is_active')
    search_fields = ('customer__username', 'lawyer__user__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_type', 'amount', 'success', 'chat', 'lawyer', 'created_at')
    list_filter = ('payment_type', 'success')
    search_fields = ('stripe_session_id',)
