from django.contrib import admin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.utils.safestring import mark_safe
from votings.models import Voting

from rooms.models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "created", "updated", "view_history")

    # Добавление ссылки на историю голосований
    def view_history(self, obj):
        return mark_safe(f'<a href="/admin/rooms/room/{obj.id}/meeting-history/">История голосований</a>')

    view_history.allow_tags = True
    view_history.short_description = "История голосований"


def meeting_history_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    meetings = Voting.objects.filter(room=room).order_by("-created")

    paginator = Paginator(meetings, 10)  # 10 записей на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/meeting_history.html", {
        "room": room,
        "page_obj": page_obj,
    })


def get_urls(self):
    urls = super(RoomAdmin, self).get_urls()
    custom_urls = [
        path("<int:room_id>/meeting-history/", self.admin_site.admin_view(meeting_history_view))
    ]
    return custom_urls + urls


RoomAdmin.get_urls = get_urls
