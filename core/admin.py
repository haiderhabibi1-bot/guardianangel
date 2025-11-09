from django.contrib import admin
from .models import CustomerProfile, LawyerProfile, GeneralQuestion


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'free_questions_left')
    search_fields = ('user__username', 'user__email')


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'speciality', 'years_experience', 'law_school', 'approved')
    list_filter = ('approved', 'speciality')
    search_fields = ('user__username', 'bar_number', 'law_school')
    readonly_fields = ('user',)

    # Optional: approve directly from admin
    actions = ['approve_selected_lawyers']

    def approve_selected_lawyers(self, request, queryset):
        queryset.update(approved=True)
    approve_selected_lawyers.short_description = "Approve selected lawyers"


@admin.register(GeneralQuestion)
class GeneralQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at')
    search_fields = ('text', 'user__username')
