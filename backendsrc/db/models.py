from django.db import models


class Calendar(models.Model):
    service_id = models.CharField(max_length=255, primary_key=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["service_id"]

class Route(models.Model):
    route_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    transport_type = models.IntegerField # Type of route (see data info for type conversions)
    capacity = models.IntegerField(null=True)

    class Meta:
        ordering = ["route_id"]
        
class Shape(models.Model):
    shape_id = models.CharField(max_length=255, primary_key=True)
    shape_pt_lat = models.FloatField()
    shape_pt_lon = models.FloatField()
    shape_pt_sequence = models.IntegerField()

    class Meta:
        ordering = ["shape_id", "shape_pt_sequence"]
        
class Station(models.Model):
    station_id = models.CharField(max_length=255, primary_key=True)
    station_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    long = models.FloatField()
    location_type = models.IntegerField() # Type of station (see data info for type conversions)

    class Meta:
        ordering = ["station_id"]
class Timetable(models.Model):
    trip_id = models.CharField(max_length=255, primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True)
    arrival_time = models.CharField(max_length=255)
    sequence = models.IntegerField()

    class Meta:
        ordering = ["trip_id"]
        unique_together = ("trip_id", "station")


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
