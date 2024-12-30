from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Community, Fitplan
from .serializers import CommunitySerializer, FitPlanSerializer
from .services.openai_service import generate_fitness_plan


class FitplanPostView(APIView):
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
    def get(self, request):
        fitplans = Fitplan.objects.all()
        serializer = FitPlanSerializer(fitplans, many=True)
        response_data = {
            "status": "success",
            "message": "Event fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

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
