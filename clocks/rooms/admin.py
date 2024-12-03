from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.utils.safestring import mark_safe
from meetings.models import Meeting

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "current_meeting", "created", "updated", "view_history")
    exclude = ("participants",)

    # Добавление ссылки на историю голосований
    def view_history(self, obj):
        return mark_safe(f'<a href="/admin/rooms/room/{obj.id}/meeting-history/">История голосований</a>')

    view_history.allow_tags = True
    view_history.short_description = "История голосований"


def meeting_history_view(request, room_id):
    meetings = Meeting.objects.filter(room=room_id)

    context = {
        "room": room_id,
        "meetings": meetings
    }

    return render(request, "admin/meeting_history.html", context)


def get_urls(self):
    urls = super(RoomAdmin, self).get_urls()
    custom_urls = [
        path("<int:room_id>/meeting-history/", self.admin_site.admin_view(meeting_history_view))
    ]
    return custom_urls + urls


RoomAdmin.get_urls = get_urls
