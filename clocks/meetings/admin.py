from django.contrib import admin

from .models import Meeting


@admin.register(Meeting)
class RoomAdmin(admin.ModelAdmin):
    exclude = ("votes", "average_score", "active",)
