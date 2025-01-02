from django.urls import path

from . import views

urlpatterns = [
    path("<str:room_name>/", views.get_messages, name="get_messages"),
]
