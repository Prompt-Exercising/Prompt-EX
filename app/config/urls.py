from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/users/", include("users.urls")),
    path("v1/fitplans/", include("fitplans.urls")),
    path("v1/chat/", include("chat.urls")),
]
