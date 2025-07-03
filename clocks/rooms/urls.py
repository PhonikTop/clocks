from django.urls import path

from .views import (
    RoomCreateView,
    RoomDetailView,
    RoomHistoryView,
    RoomListView,
    RoomParticipantsView,
)

urlpatterns = [
    path("", RoomCreateView.as_view(), name="room_create"),
    path("list/", RoomListView.as_view(), name="room_list"),
    path("<int:pk>/history/", RoomHistoryView.as_view(), name="room_history"),
    path("<int:id>/", RoomDetailView.as_view(), name="room_detail"),
    path("<int:id>/participants/", RoomParticipantsView.as_view(), name="room_participants"),
]
