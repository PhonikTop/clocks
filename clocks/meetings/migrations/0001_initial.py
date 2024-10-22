# Generated by Django 5.1 on 2024-09-05 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=200)),
                ('votes', models.JSONField(default=dict)),
                ('average_score', models.FloatField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
