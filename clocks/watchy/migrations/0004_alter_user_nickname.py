# Generated by Django 5.1 on 2024-08-23 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("watchy", "0003_user_nickname_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="nickname",
            field=models.CharField(default="Игрок", max_length=100),
        ),
    ]
