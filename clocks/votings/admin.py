from django.contrib import admin

from votings.models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    exclude = ("votes", "average_score", "active",)
