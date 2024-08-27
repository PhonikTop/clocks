from django.urls import path

from . import views

urlpatterns = [
    path("join-room/", views.join_room, name="join_room"),
    path("current/", views.get_current_user, name="get_current_user"),
]
