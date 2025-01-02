from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserInfoSerializer, UserSerializer
from users.services.token_service import create_jwt_response


class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["POST"],
        summary="일반 회원가입",
        description="이메일, 이름, 비밀번호 사용한 회원가입입니다.",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="회원가입 실패"),
        },
    )
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

    @extend_schema(
        methods=["POST"],
        summary="일반 로그인",
        description="로그인을 시도해주세요",
        request=inline_serializer(
            name="UserLoginRequest",
            fields={
                "email": serializers.EmailField(help_text="User's email address"),
                "password": serializers.CharField(help_text="User's password"),
            },
        ),
        responses={
            200: inline_serializer(
                name="UserLoginResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "name": serializers.CharField(),
                    "email": serializers.EmailField(),
                },
            ),
            400: OpenApiResponse(description="Invalid credentials"),
            401: OpenApiResponse(description="Unauthorized or inactive user"),
        },
    )
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
    @extend_schema(
        methods=["POST"],
        summary="로그아웃",
        description="로그아웃 요청 시 JWT 쿠키 삭제됩니다.",
        responses={
            200: OpenApiResponse(description="Logout success message"),
        },
    )
    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response(
            data={"message": "로그아웃 성공"}, status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: UserInfoSerializer,
            404: OpenApiParameter("detail", "string", description="User not found"),
        },
    )
    def get(self, request):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)
