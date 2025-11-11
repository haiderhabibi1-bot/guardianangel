from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_add_question_text_to_publicquestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="specialty",
            field=models.CharField(max_length=255, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="profile",
            name="practice_start_year",
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="bio",
            field=models.TextField(max_length=1000, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="profile",
            name="fee_per_chat",
            field=models.DecimalField(
                max_digits=8,
                decimal_places=2,
                null=True,
                blank=True,
            ),
        ),
    ]
