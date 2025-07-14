from django.contrib import admin

from meetings.models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    exclude = ("votes", "average_score", "active",)
