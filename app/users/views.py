import os

from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserInfoSerializer, UserSerializer
from users.services.token_service import create_jwt_response

from .models import EmailVerification


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
            user = serializer.save(is_active=False)
            email_verification = EmailVerification.objects.create(user=user)
            current_site = get_current_site(request)
            mail_subject = "이메일 인증을 완료하세요."
            message_html = render_to_string(
                "emails/activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "token": email_verification.token,
                },
            )

            message_text = strip_tags(message_html)

            email = EmailMessage(
                subject=mail_subject,
                body=message_text,
                from_email=os.getenv("EMAIL_HOST_USER"),
                to=[user.email],
            )
            email.content_subtype = "html"
            email.body = message_html

            email.send()

            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return Response(
                {"detail": "회원가입 실패"}, status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    methods=["GET"],
    summary="이메일 인증",
    description="이메일 인증을 완료합니다. 해당 URL을 클릭하면 인증이 완료되고 사용자가 활성화됩니다.",
    responses={
        200: OpenApiResponse(description="이메일 인증이 완료되었습니다."),
        400: OpenApiResponse(description="잘못된 토큰입니다."),
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def activate_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token)
    except ObjectDoesNotExist:
        return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    if verification.verified_at:
        return Response({"detail": "이미 인증되었습니다."}, status=status.HTTP_200_OK)

    verification.verified_at = now()
    verification.save()

    verification.user.is_active = True
    verification.user.save()

    return Response(
        {"detail": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK
    )


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
