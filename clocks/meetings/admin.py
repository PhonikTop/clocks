from django.contrib import admin

from clocks.meetings.models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    exclude = ("votes", "average_score", "active",)
