from django.db import models
from django.utils import timezone

class DataItem(models.Model):
    author = models.ForeignKey('auth.User')
    created_date = models.DateTimeField(default=timezone.now)
    
    def publish(self):
        self.save()

    def __str__(self):
        return self.author

    class Meta:
        abstract = True

