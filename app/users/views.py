import logging

from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserInfoSerializer, UserSerializer
from users.services.token_service import create_jwt_response

logger = logging.getLogger(__name__)


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            return response
        except Exception as e:
            print(f"Error: {e}")


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "이메일과 비밀번호는 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "잘못된 이메일입니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

        if user.check_password(password):
            return create_jwt_response(user, request)
        else:
            return Response(
                {"detail": "비밀번호가 틀렸습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            token = RefreshToken(refresh_token)  # type: ignore
            token.blacklist()

        response = Response(
            data={"message": "로그아웃 성공"}, status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)
