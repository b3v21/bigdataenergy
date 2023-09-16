from rest_framework import serializers
from db.models import (
    Calendar,
    Route,
    Shape,
    Station,
    Trip,
    Timetable,
    SimulationOutput,
    TravelTimes,
)


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = [
            "service_id",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "start_date",
            "end_date",
        ]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["route_id", "name", "transport_type", "capacity"]


class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = [
            "station_id",
            "station_code",
            "name",
            "lat",
            "long",
            "location_type",
            "suburb",
        ]


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ["trip_id", "route_id", "service_id", "shape_id"]


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ["trip_id", "station", "arrival_time", "sequence"]


class SimulationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationOutput
        fields = ["simulation_id"]


class TravelTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTimes
        fields = ["traveltime_id", "from_station", "to_station", "duration"]
