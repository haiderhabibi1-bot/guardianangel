from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_add_question_text_to_publicquestion"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Main profile for both customers and lawyers
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                # Customer / Lawyer role
                (
                    "role",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("customer", "Customer"),
                            ("lawyer", "Lawyer"),
                        ],
                    ),
                ),
                # Lawyer approval flag
                (
                    "is_approved",
                    models.BooleanField(default=False),
                ),
                # Lawyer identity + bar info
                (
                    "full_name",
                    models.CharField(max_length=150, blank=True),
                ),
                (
                    "bar_number",
                    models.CharField(max_length=100, blank=True),
                ),
                (
                    "bar_certificate",
                    models.FileField(
                        upload_to="bar_certificates/",
                        blank=True,
                        null=True,
                    ),
                ),
                # Extra lawyer info
                (
                    "specialty",
                    models.CharField(max_length=255, blank=True),
                ),
                (
                    "practice_start_year",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        max_length=1000,
                        blank=True,
                    ),
                ),
                (
                    "fee_per_chat",
                    models.DecimalField(
                        max_digits=8,
                        decimal_places=2,
                        blank=True,
                        null=True,
                    ),
                ),
                # Link to Django's User
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),

        # Simple billing profile linked to user
        migrations.CreateModel(
            name="BillingProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "billing_method",
                    models.CharField(
                        max_length=255,
                        blank=True,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="billing",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
