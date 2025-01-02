from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Community, Fitplan
from .serializers import CommunitySerializer, FitPlanSerializer
from .services.openai_service import generate_fitness_plan


class FitplanPostView(APIView):
    @extend_schema(
        methods=["POST"],
        summary="운동 계획 생성",
        description="사용자의 데이터를 바탕으로 운동 계획을 생성합니다.",
        request=FitPlanSerializer,
        responses={
            201: FitPlanSerializer,
            400: OpenApiResponse(description="운동 계획 생성 실패"),
        },
    )
    def post(self, request):
        user = request.user

        data = request.data.copy()
        data["user"] = user.id

        serializer = FitPlanSerializer(data=data)
        if serializer.is_valid():
            fitplan = serializer.save(user=user)

            user_data = {
                "weight": fitplan.weight,
                "target_weight": fitplan.target_weight,
                "chest": fitplan.chest,
                "waist": fitplan.waist,
                "thigh": fitplan.thigh,
                "period": fitplan.period,
            }
            ai_result = generate_fitness_plan(user_data)
            response_data = {
                "status": "success",
                "message": "운동 계획 생성 완료",
                "data": serializer.data,
                "fitness_plan": ai_result,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FitplanListView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="운동 계획 리스트",
        description="모든 운동 계획을 조회합니다.",
        responses={
            200: FitPlanSerializer(many=True),
            400: OpenApiResponse(description="운동 계획 리스트 조회 실패"),
        },
    )
    def get(self, request):
        fitplans = Fitplan.objects.all()
        serializer = FitPlanSerializer(fitplans, many=True)
        response_data = {
            "status": "success",
            "message": "Event fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        methods=["DELETE"],
        summary="운동 계획 삭제",
        description="운동 계획을 ID로 삭제합니다.",
        responses={
            200: OpenApiResponse(description="운동 계획 삭제 성공"),
            400: OpenApiResponse(description="운동 계획 삭제 실패"),
            404: OpenApiResponse(description="운동 계획을 찾을 수 없음"),
        },
    )
    def delete(self, request):
        fitplan_id = request.data.get("id")
        if not fitplan_id:
            return Response(
                {"status": "error", "message": "Fitplan ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fitplan = Fitplan.objects.get(id=fitplan_id)
            fitplan.delete()
            return Response(
                {
                    "status": "success",
                    "message": f"Fitplan with id {fitplan_id} deleted successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Fitplan.DoesNotExist:
            return Response(
                {"status": "error", "message": "Fitplan not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CommunityListView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="커뮤니티 리스트",
        description="모든 커뮤니티를 조회합니다.",
        responses={
            200: CommunitySerializer(many=True),
            400: OpenApiResponse(description="커뮤니티 리스트 조회 실패"),
        },
    )
    def get(self, request):
        communities = Community.objects.all()
        serializer = CommunitySerializer(communities, many=True)
        response_data = {
            "status": "success",
            "message": "Community fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CommunityPostView(APIView):
    @extend_schema(
        methods=["POST"],
        summary="커뮤니티 생성",
        description="새로운 커뮤니티를 생성합니다.",
        request=CommunitySerializer,
        responses={
            201: CommunitySerializer,
            400: OpenApiResponse(description="커뮤니티 생성 실패"),
        },
    )
    def post(self, request):
        user = request.user
        data = request.data.copy()
        data["user"] = user.id

        serializer = CommunitySerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {"status": "success", "message": "Community created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityDetailView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="커뮤니티 상세",
        description="특정 커뮤니티의 상세 정보를 조회합니다.",
        parameters=[
            OpenApiParameter(
                "community_id",
                int,
                description="커뮤니티 ID",
                required=True,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: CommunitySerializer,
            404: OpenApiResponse(description="커뮤니티를 찾을 수 없음"),
        },
    )
    def get(self, request, community_id):
        try:
            community = Community.objects.get(user=request.user, id=community_id)
            serializer = CommunitySerializer(community)
            return Response(
                {
                    "status": "success",
                    "message": "Community fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Community.DoesNotExist:
            return Response(
                {"status": "error", "message": "Community not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        methods=["PATCH"],
        summary="커뮤니티 업데이트",
        description="커뮤니티 정보를 업데이트합니다.",
        parameters=[
            OpenApiParameter(
                "community_id",
                int,
                description="커뮤니티 ID",
                required=True,
                location=OpenApiParameter.PATH,
            )
        ],
        request=CommunitySerializer,
        responses={
            200: CommunitySerializer,
            400: OpenApiResponse(description="커뮤니티 업데이트 실패"),
        },
    )
    def patch(self, request, community_id):
        try:
            community = Community.objects.get(user=request.user, id=community_id)
        except Community.DoesNotExist:
            return Response(
                {"status": "error", "message": "Community not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommunitySerializer(community, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Community updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": "error", "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommunityDeleteView(APIView):
    @extend_schema(
        methods=["DELETE"],
        summary="커뮤니티 삭제",
        description="커뮤니티를 ID로 삭제합니다.",
        parameters=[
            OpenApiParameter(
                "community_id",
                int,
                description="커뮤니티 ID",
                required=True,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: OpenApiResponse(description="커뮤니티 삭제 성공"),
            404: OpenApiResponse(description="커뮤니티를 찾을 수 없음"),
        },
    )
    def delete(self, request, community_id):
        try:
            community = Community.objects.get(user=request.user, id=community_id)
            community_title = community.title
            community.delete()
            return Response(
                {
                    "status": "success",
                    "message": f"Community with id {community_title} deleted successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Community.DoesNotExist:
            return Response(
                {"status": "error", "message": "Community not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
