from django.db import models

# Create your models here.
class Station(models.Model):
    station_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    long = models.FloatField()

    class Meta:
        ordering = ['station_id']