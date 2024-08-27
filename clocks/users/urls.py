import views
from django.urls import path

urlpatterns = [
    path("user/join-room", views.join_room, name="join_room"),
    path("user/current", views.get_current_user, name="get_current_user"),
]
