from django.db import models

# Create your models here.
class Station(models.Model):
    station_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    long = models.FloatField()

    def __str__(self):
        return self.headline
    
class Route(models.Model):
    route_id = models.IntegerField(primary_key=True)
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    station_seq = models.IntegerField(default=1)
    start = models.BinaryField()
    stop = models.BinaryField()
    
class Timetable(models.Model):
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    arrival_times = models.CharField(max_length=255)

all_stations = Station.objects.all()