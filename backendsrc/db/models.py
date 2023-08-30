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
    type = models.CharField(max_length=255)  # Type of route (i.e. bus, train, etc.)
    start = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="start")
    end = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="end")
    station_sequence = models.CharField(max_length=255)

    class Meta:
        ordering = ["route_id"]

    def get(self):
        return {
            "route_id": self.route_id,
            "name": self.name,
            "type": self.type,
            "start": self.start,
            "end": self.end,
            "station_sequence": self.station_sequence,
        }


class Timetable(models.Model):
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    arrival_times = models.CharField(max_length=255)

    class Meta:
        ordering = ["station_id", "route_id"]
        unique_together = ("station_id", "route_id")

    def get(self):
        return {
            "station_id": self.station_id,
            "route_id": self.route_id,
            "arrival_times": self.arrival_times,
        }


class SimulationOutput(models.Model):
    simulation_id = models.IntegerField(primary_key=True)
