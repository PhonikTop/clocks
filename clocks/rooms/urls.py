from django.urls import path

from . import views

# urlpatterns = [
#     path("rooms", views.get_rooms, name="get_rooms"),
#     path("room", views.create_room, name="create_room"),
#     path("room/get/<int:room_id>", views.get_room, name="get_room"),
#     path("room/del/<int:room_id>", views.delete_room, name="delete_room"),
#     path("room/<int:room_id>/participants", views.get_room_participants, name="get_room_participants"),
#     path("room/<int:room_id>/history", views.get_room_history, name="get_room_history"),
# ]

urlpatterns = [
    path("", views.create_room, name="create_room"),
    path("list/", views.get_rooms, name="get_rooms"),
    path("get/<int:room_id>/", views.get_room, name="get_room"),
    path("delete/<int:room_id>/", views.delete_room, name="delete_room"),
    path("<int:room_id>/participants/", views.get_room_participants, name="get_room_participants"),
    path("<int:room_id>/history/", views.get_room_history, name="get_room_history"),
]
