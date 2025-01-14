from django.urls import path

from .views import JoinRoomView, UserInfoView

urlpatterns = [
    path("join/<int:pk>/", JoinRoomView.as_view(), name="join_room"),
    path("<int:pk>/", UserInfoView.as_view(), name="user_info"),
]
