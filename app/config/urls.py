from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/users/", include("users.urls")),
    path("v1/fitplans/", include("fitplans.urls")),
    path("v1/chat/", include("chat.urls")),
    path('v1/schema/', SpectacularAPIView.as_view(), name='schema'),  # OpenAPI 스키마
    path('v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # Redoc UI
]
