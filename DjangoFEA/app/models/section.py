from django.db import models
from app.models import DataItem

class Section(DataItem):
    E = models.FloatField()
    A = models.FloatField()
    J = models.FloatField()
    ro = models.FloatField()