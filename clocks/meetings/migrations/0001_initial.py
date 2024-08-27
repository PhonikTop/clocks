# Generated by Django 5.1 on 2024-08-27 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Session",
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
                ("task_name", models.CharField(max_length=200)),
                ("votes", models.JSONField(default=dict)),
                ("average_score", models.FloatField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("completed", "Completed")],
                        default="active",
                        max_length=20,
                    ),
                ),
            ],
        ),
    ]