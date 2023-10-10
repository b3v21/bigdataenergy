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
    ItineraryCache,
)


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        "__all__"


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        "__all__"


class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        "__all__"


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        "__all__"


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = "__all__"


class TravelTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTimes
        fields = "__all__"


class SimulationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationOutput
        fields = "__all__"


class BusTimeOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusTimeOut
        fields = "__all__"


class PassengerChangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerChanges
        fields = "__all__"


class BusOnRouteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusOnRouteInfo
        fields = "__all__"


class StationSimSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationSim
        fields = "__all__"
        depth = 1


class RouteSimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteSim
        fields = "__all__"
        depth = 2


class ItinerarySimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItinerarySim
        fields = "__all__"


class RouteInItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteInItinerary
        fields = "__all__"


class ItineraryCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryCache
        fields = "__all__"


class SimOutputForFrontendSerializer(serializers.Serializer):
    routes = RouteSimSerializer(many=True, read_only=True)
    stations = StationSimSerializer(many=True, read_only=True)
    itinerary = ItinerarySimSerializer(many=True, read_only=True)

    class Meta:
        Model = SimulationOutput
        fields = ("routes", "stations", "itinerary")
