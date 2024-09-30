from django.contrib import admin

from clocks.rooms.models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    exclude = ("participants",)
