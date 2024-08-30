from django.urls import path

from .consumers import RoomConsumer

ws_urlpatterns = [
    path("ws/room/<int:room_id>", RoomConsumer.as_asgi())
]
