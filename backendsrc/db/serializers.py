from rest_framework import serializers
from db.models import Station, Route, Timetable, SimulationOutput, TravelTimes


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["station_id", "name", "lat", "long"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "route_id",
            "translink_id" "name",
            "transport_type",
            "capacity",
        ]


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = [
            "timetable_id",
            "station_id",
            "route_id" "translink_id",
            "sequence",
            "arrival_times",
        ]


class SimulationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationOutput
        fields = ["simulation_id"]


class TravelTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTimes
        fields = ["traveltime_id", "from_station", "to_station", "duration"]
