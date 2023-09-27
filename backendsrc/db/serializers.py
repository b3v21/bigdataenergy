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
    BusTimeOut,
    PassengerChanges,
    BusOnRouteInfo,
    StationSim,
    RouteSim,
    ItinerarySim,
    RouteInItinerary,
    ItineraryCache
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


class BusTimeOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusTimeOut
        fields = ["bustimeout_id", "stop_name", "time"]


class PassengerChangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerChanges
        fields = ["passenger_changes_id", "time", "passenger_count"]


class BusOnRouteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusOnRouteInfo
        fields = ["bus_id", "bus_timeout", "bus_passenger_changes"]


class StationSimSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationSim
        fields = ["station_id", "name", "pos", "passenger_count"]


class RouteSimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteSim
        fields = ["route_sim_id", "route_id", "method", "buses_on_route", "stations"]

class ItinerarySimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItinerarySim
        fields = ["itinerary_id", "routes"]
        
class RouteInItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteInItinerary
        fields = ["start", "end"]
        
class ItineraryCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteInItinerary
        fields = ["itinerary_id","route","sequence"]
