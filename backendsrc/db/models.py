from django.db import models


# Create your models here.
class Station(models.Model):
    station_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    long = models.FloatField()

    class Meta:
        ordering = ["station_id"]

    def get(self):
        return {
            "station_id": self.station_id,
            "name": self.name,
            "lat": self.lat,
            "long": self.long,
        }


class Route(models.Model):
    route_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    start = models.BinaryField()
    end = models.BinaryField()
    station_sequence = models.IntegerField()

    class Meta:
        ordering = ["route_id"]

    def get(self):
        return {
            "route_id": self.route_id,
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "station_sequence": self.station_sequence,
        }


class Timetable(models.Model):
    station_id = models.ForeignKey()
    route_id = models.ForeignKey()
    arrival_times = models.CharField()

    class Meta:
        ordering = ["station_id"]
        unique_together = ("station_id", "route_id")

    def get(self):
        return {
            "station_id": self.station_id,
            "route_id": self.route_id,
            "arrival_times" : self.arrival_times
        }
