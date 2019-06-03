import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Distance(models.Model):
    distance = models.FloatField()
    pub_date = models.DateTimeField('date published')

    class Meta:
      verbose_name_plural = "sensor"

    # def __str__(self):
    #     return self.distance

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
