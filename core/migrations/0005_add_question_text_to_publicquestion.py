from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_add_customer_to_publicquestion"),  # your previous migration
    ]

    operations = [
        migrations.AddField(
            model_name="publicquestion",
            name="question_text",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
