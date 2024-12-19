from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Fitplan
from .serializers import FitPlanSerializer
from .services import generate_fitness_plan


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
