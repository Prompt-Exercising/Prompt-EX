from rest_framework import serializers
from .models import Fitplan

class FitPlanSerializer(serializers.ModelSerializer):
    goal = serializers.StringRelatedField()

    class Meta:
        model = Fitplan
        fields = ['id', 'date', 'weight','user', 'target_weight', 'goal', 'chest', 'waist', 'thigh', 'period']
        read_only_fields = ['id', 'date']