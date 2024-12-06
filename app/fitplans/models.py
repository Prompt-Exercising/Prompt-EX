from django.db import models


class Size(models.Model):
    weight = models.FloatField()
    chest = models.FloatField()
    waist = models.FloatField()
    thigh = models.FloatField()
    goal = models.CharField(max_length=100)
    period = models.PositiveIntegerField()
