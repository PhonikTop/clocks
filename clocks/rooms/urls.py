from django.urls import path

from . import views
from .views import RoomCreateView, RoomDetailView, RoomHistoryView, RoomListView, RoomParticipantsView

urlpatterns = [
    path("", RoomCreateView.as_view(), name="room_create"),  # GET для списка комнат, POST для создания новой

    path("list/", RoomListView.as_view(), name="room_list"),  # GET для списка комнат, POST для создания новой

    path("<int:room_id>/", RoomDetailView.as_view(), name="room_detail"),
    # GET для получения информации о комнате, DELETE для удаления

    path("<int:room_id>/participants/", RoomParticipantsView.as_view(), name="room_participants"),
    # GET для списка участников

    path("<int:room_id>/history/", RoomHistoryView.as_view(), name="room_history"),  # GET для истории сессий
]

# urlpatterns = [
#     path("", views.create_room, name="create_room"),
#
#     path("list/", views.get_rooms, name="get_rooms"),
#
#     path("get/<int:room_id>/", views.get_room, name="get_room"),
#     path("delete/<int:room_id>/", views.delete_room, name="delete_room"),
#
#     path("<int:room_id>/participants/", views.get_room_participants, name="get_room_participants"),
#
#     path("<int:room_id>/history/", views.get_room_history, name="get_room_history"),
# ]
