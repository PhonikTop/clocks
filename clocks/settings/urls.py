from django.shortcuts import render
from django.urls import include, path


def index(request):
    return render(request, "index.html")
    print("index")


urlpatterns = [
    path("api/v1/", include("api.urls")),
    path("", index),
]
