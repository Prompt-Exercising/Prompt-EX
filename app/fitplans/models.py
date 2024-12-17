from django.db import models
from common.models import CommonModel
from users.models import User
from django.core.validators import MinValueValidator

class Goal(models.Model):
    goal = models.CharField(max_length=100)

    def __str__(self):
        return self.goal

class Fitplan(CommonModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField(validators=[MinValueValidator(0)], help_text="단위: kg")
    target_weight = models.FloatField(validators=[MinValueValidator(0)], default=0.0, help_text="목표 체중 (단위: kg)")
    chest = models.FloatField(validators=[MinValueValidator(0)], help_text="단위: 인치")
    waist = models.FloatField(validators=[MinValueValidator(0)], help_text="단위: 인치")
    thigh = models.FloatField(validators=[MinValueValidator(0)], help_text="단위: 인치")
    goal = models.ForeignKey("Goal", on_delete=models.CASCADE, null=True, blank=True)
    period = models.PositiveIntegerField(help_text="목표 달성 기간 (일)")

    class Meta:
        ordering = ['-date']