from django.urls import path

from .views import JoinRoomView

urlpatterns = [
    path("join/<int:pk>/", JoinRoomView.as_view(), name="join_room"),
]
