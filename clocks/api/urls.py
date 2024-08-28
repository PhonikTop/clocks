from django.urls import include, path

# Import views from all api applications
from meetings import views as meetings

urlpatterns = [
    path("user/", include("users.urls")),
    path("room/", include("rooms.urls")),
    path("meeting/", include("meetings.urls")),
]
