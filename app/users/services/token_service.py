from django.contrib.auth import login
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer


def create_jwt_response(user, request):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    login(request, user)
    user.last_login = now()
    user.save()

    response = Response(
        {"detail": "로그인 성공", "user": UserSerializer(user).data},
        status=HTTP_200_OK,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Strict",
        max_age=3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=False,
        samesite="Strict",
        max_age=86400,
    )

    return response
