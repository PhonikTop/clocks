from django.urls import path

from users.views import JoinRoomView, UserInfoView, UserKickView

urlpatterns = [
    path("join/<int:pk>/", JoinRoomView.as_view(), name="join_room"),
    path("<int:pk>/", UserInfoView.as_view(), name="user_info"),
    path("<int:pk>/kick", UserKickView.as_view(), name="user_kick")
]
