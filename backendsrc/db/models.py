from django.db import models
from datetime import datetime


class Calendar(models.Model):
    service_id = models.CharField(max_length=255, primary_key=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)

    class Meta:
        ordering = ["service_id"]


class Route(models.Model):
    route_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    transport_type = (
        models.IntegerField()
    )  # Type of route (see data info for type conversions)
    capacity = models.IntegerField(null=True)

    class Meta:
        ordering = ["route_id"]


class Shape(models.Model):
    shape_id = models.CharField(max_length=255)
    shape_pt_lat = models.FloatField()
    shape_pt_lon = models.FloatField()
    shape_pt_sequence = models.IntegerField()

    class Meta:
        ordering = ["shape_id", "shape_pt_sequence"]
        unique_together = ("shape_id", "shape_pt_sequence")


class Station(models.Model):
    station_id = models.CharField(max_length=255, primary_key=True)
    station_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    long = models.FloatField()
    location_type = (
        models.IntegerField()
    )  # Type of station (see data info for type conversions)
    suburb = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ["station_id"]


class Trip(models.Model):
    trip_id = models.CharField(max_length=255, primary_key=True)
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    shape_id = models.ForeignKey(Shape, on_delete=models.CASCADE)

    class Meta:
        ordering = ["trip_id", "route_id", "service_id", "shape_id"]


class Timetable(models.Model):
    trip_id = models.ForeignKey(Trip, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True)
    arrival_time = models.TimeField(max_length=255)
    sequence = models.IntegerField()

    class Meta:
        ordering = ["trip_id"]
        unique_together = ("trip_id", "station", "arrival_time", "sequence")


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
