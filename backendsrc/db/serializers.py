from rest_framework import serializers
from db.models import Station, Route, Timetable


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["station_id", "name", "lat", "long"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["route_id", "station_id", "name", "transport_type", "next_st", "prev_st"]


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ["station_id", "route_id", "arrival_times"]
