from django.urls import path

from .views import (
    RoomCreateView,
    RoomDetailView,
    RoomListView,
    RoomParticipantsView,
)

urlpatterns = [
    path("", RoomCreateView.as_view(), name="room_create"),
    path("list/", RoomListView.as_view(), name="room_list"),
    path("<int:pk>/", RoomDetailView.as_view(), name="room_detail"),
    path("<int:pk>/participants/", RoomParticipantsView.as_view(), name="room_participants"),
]
