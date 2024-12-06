from django.urls import path

from .views import LoginView, LogoutView, SignUpView, UserView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", UserView.as_view(), name="user"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
