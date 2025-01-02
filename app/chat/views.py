from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import Message

@extend_schema(
    methods=["GET"],
    summary="특정 방의 메시지 조회",
    description="주어진 방의 최근 50개의 메시지를 조회합니다.",
    parameters=[
        OpenApiParameter("room_name", str, description="방 이름", required=True)
    ],
    responses={
        200: OpenApiResponse(
            description="메시지 조회 성공",
            examples=[
                {
                    "messages": [
                        {"user__name": "User1", "content": "Hello!", "timestamp": "2025-01-01T00:00:00Z"},
                        {"user__name": "User2", "content": "Hi there!", "timestamp": "2025-01-01T01:00:00Z"},
                    ]
                }
            ],
        ),
        404: OpenApiResponse(description="방을 찾을 수 없음"),
    },
)


def get_messages(request, room_name):
    messages = Message.objects.filter(room__name=room_name).order_by("-timestamp")[:50]
    return JsonResponse(
        {"messages": list(messages.values("user__name", "content", "timestamp"))}
    )
