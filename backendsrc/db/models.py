from django.db import models


# Create your models here.
class Station(models.Model):
    station_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    long = models.FloatField()

    class Meta:
        ordering = ["station_id"]


class Route(models.Model):
    route_id = models.IntegerField(primary_key=True)
    translink_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    transport_type = models.CharField(
        max_length=255
    )  # Type of route (i.e. bus, train, etc.)
    capacity = models.IntegerField(null=True)

    class Meta:
        ordering = ["route_id"]
        unique_together = ("route_id", "translink_id")


class Timetable(models.Model):
    timetable_id = models.IntegerField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True)
    translink_trip_id = models.CharField(max_length=255)
    translink_trip_id_simple = models.IntegerField()
    arrival_time = models.TimeField()
    sequence = models.IntegerField()

    class Meta:
        ordering = ["timetable_id"]


class SimulationOutput(models.Model):
    simulation_id = models.IntegerField(primary_key=True)


class TravelTimes(models.Model):
    traveltime_id = models.IntegerField(primary_key=True)
    from_station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="from_station"
    )
    to_station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="to_station"
    )
    duration = models.FloatField(default=0)
