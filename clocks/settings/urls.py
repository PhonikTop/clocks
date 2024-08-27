from django.urls import include, path
from watchy import views

urlpatterns = [
    path("api/v1/", include("api.urls")),
]
