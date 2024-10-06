from django.urls import include, path

urlpatterns = [
    path("user/", include("users.urls")),
    path("room/", include("rooms.urls")),
    path("meeting/", include("meetings.urls")),
]
