from django.urls import path

from .views import CurrentUserView, JoinRoomView

urlpatterns = [
    path("join/", JoinRoomView.as_view(), name="join_room"),
    path("current/", CurrentUserView.as_view(), name="get_current_user"),
]
