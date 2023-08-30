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
    station_id = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    transport_type = models.CharField(
        max_length=255
    )  # Type of route (i.e. bus, train, etc.)
    capacity = models.IntegerField(null=True)
    next_st = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="next")
    prev_st = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="prev")

    class Meta:
        ordering = ["route_id"]
        unique_together = ("route_id", "station_id")

    def get(self):
        return {
            "route_id": self.route_id,
            "station_id": self.station_id,
            "name": self.name,
            "transport_type": self.transport_type,
            "next_st": self.next_st,
            "end_st": self.end_st,
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
            "station_id": self,
            "route_id": self.route_id,
            "arrival_times": self.arrival_times,
        }


class SimulationOutput(models.Model):
    simulation_id = models.IntegerField(primary_key=True)


class TravelTimes(models.Model):
    traveltime_id = models.IntegerField(primary_key=True)
    from_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="from_station")
    to_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="to_station")
    duration = models.FloatField(default=0)
