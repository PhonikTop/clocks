from django.urls import path

from rooms.views import (
    GetRoomTimer,
    ResetRoomTimer,
    RoomCreateView,
    RoomDetailView,
    RoomListView,
    RoomParticipantsView,
    SetRoomTimer,
)

urlpatterns = [
    path("", RoomCreateView.as_view(), name="room_create"),
    path("list/", RoomListView.as_view(), name="room_list"),
    path("<int:pk>/", RoomDetailView.as_view(), name="room_detail"),
    path("<int:pk>/participants/", RoomParticipantsView.as_view(), name="room_participants"),
    path("<int:pk>/timer_start", SetRoomTimer.as_view(), name="set_room_timer"),
    path("<int:pk>/get_timer_start", GetRoomTimer.as_view(), name="get_room_timer"),
    path("<int:pk>/reset_timer_start", ResetRoomTimer.as_view(), name="reset_room_timer"),
]
