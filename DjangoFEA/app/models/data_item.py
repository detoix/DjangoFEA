from django.db import models
from django.utils import timezone

class DataItem(models.Model):
    author = models.ForeignKey('auth.User')
    project_name = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)
    
    def publish(self):
        self.save()

    def __str__(self):
        return self.project_name

    class Meta:
        abstract = True

