from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# def Test_Page(request, room_id):
#     return render(request, "index.html", {"room_id": room_id})


urlpatterns = [
    path("api/v1/", include("api.urls")),
    # path("room/<int:room_id>/", Test_Page),
    path("grappelli/", include("grappelli.urls")),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
