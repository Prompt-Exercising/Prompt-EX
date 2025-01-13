from django.urls import path

from . import views

urlpatterns = [
    path("<int:room_id>/", views.get_messages, name="get_messages"),
    path("roomlist/", views.get_roomlist, name="get_roomlist"),
]
