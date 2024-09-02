from django.urls import re_path

from .consumers import RoomConsumer

ws_urlpatterns = [
    re_path(r"ws/room/(?P<room_id>\d+)/$", RoomConsumer.as_asgi()),
]