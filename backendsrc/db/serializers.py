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
    TransporterTimeOut,
    PassengerChanges,
    TransporterOnRouteInfo,
    StationSim,
    RouteSim,
    ItinerarySim,
    RouteInItinCache,
    ItineraryCache,
    Walk,
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


class TravelTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTimes
        fields = ["traveltime_id", "from_station", "to_station", "duration"]


class SimulationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationOutput
        fields = ["simulation_id", "route_id", "station_id", "itinerary_id"]
        depth = 3


class TransporterTimeOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransporterTimeOut
        fields = ["transporter_timeout_id", "stop_name", "time"]


class PassengerChangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerChanges
        fields = ["passenger_changes_id", "time", "passenger_count"]


class TransporterOnRouteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransporterOnRouteInfo
        fields = [
            "transporter_id",
            "transporter_timeout",
            "transporter_passenger_changes",
        ]


class StationSimSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationSim
        fields = ["station_id", "name", "pos", "passenger_count"]


class RouteSimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteSim
        fields = [
            "route_sim_id",
            "route_id",
            "method",
            "transporters_on_route",
            "stations",
        ]


class ItinerarySimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItinerarySim
        fields = ["itinerary_id", "routes"]


class RouteInItinCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteInItinCache
        fields = ["route_in_itin_id", "itinerary", "route", "walk", "sequence"]


class ItineraryCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteInItinCache
        fields = ["itinerary_id", "start_station", "end_station", "start_time"]


class Walk(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = ["walk_id", "from_station", "to_station", "duration"]
