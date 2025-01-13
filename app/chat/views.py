from django.http import JsonResponse
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view

from users.models import User

from .models import Message


@extend_schema(
    methods=["GET"],
    summary="특정 방의 메시지 조회",
    description="주어진 방의 최근 50개의 메시지를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="room_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="방 번호",
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            description="메시지 조회 성공",
            examples=[
                {
                    "messages": [
                        {
                            "user__name": "User1",
                            "content": "Hello!",
                            "timestamp": "2025-01-01T00:00:00Z",
                        },
                        {
                            "user__name": "User2",
                            "content": "Hi there!",
                            "timestamp": "2025-01-01T01:00:00Z",
                        },
                    ]
                }
            ],
        ),
        404: OpenApiResponse(description="방을 찾을 수 없음"),
    },
)
@api_view(["GET"])
def get_messages(request, room_id):
    messages = Message.objects.filter(room__id=room_id).order_by("-timestamp")[:50]
    return JsonResponse(
        {"messages": list(messages.values("user__name", "content", "timestamp"))}
    )


@extend_schema(
    methods=["GET"],
    summary="참가한 채팅방 리스트 조회",
    description="로그인한 사용자가 참가했던 모든 채팅방 리스트를 반환합니다.",
    responses={
        200: OpenApiResponse(
            description="채팅방 리스트 조회 성공",
            examples=[
                {
                    "roomlist": [
                        {
                            "id": "1",
                            "created_at": "2025-01-01T00:00:00Z",
                        },
                        {
                            "id": "2",
                            "created_at": "2025-01-02T00:00:00Z",
                        },
                    ]
                }
            ],
        ),
        401: OpenApiResponse(description="인증 실패"),
    },
)
@api_view(["GET"])
def get_roomlist(request):
    try:
        chat_rooms = request.user.chat_rooms.all().order_by("-created_at")
        room_list = list(chat_rooms.values("id", "created_at"))

        return JsonResponse({"roomlist": room_list})
    except Exception as e:
        return JsonResponse(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
