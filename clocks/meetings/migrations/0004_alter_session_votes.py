# Generated by Django 5.1 on 2024-08-27 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0003_remove_session_status_session_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="votes",
            field=models.JSONField(default=dict),
        ),
    ]