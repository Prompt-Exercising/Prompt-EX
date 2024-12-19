from django.contrib import admin

from fitplans.models import Fitplan, Goal


@admin.register(Fitplan)
class FitplanAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "weight", "target_weight", "goal", "period")


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "goal")
    search_fields = ("goal",)
