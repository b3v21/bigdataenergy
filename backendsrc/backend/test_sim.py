from sim import (
    Station,
    Trip,
    BusRoute,
    Walk,
    Itinerary,
    Suburb,
    ITINERARIES,
    run_simulation,
)
from simpy import Environment
from db.models import (
    Station as StationM,
    Route as RouteM,
    Timetable as TimetableM,
    Trip as TripM,
    Shape as ShapeM,
    Calendar as CalendarM,
    SimulationOutput,
    RouteSim,
    StationSim,
    ItinerarySim,
    BusOnRouteInfo,
    BusTimeOut,
    PassengerChanges,
)  # noqa: E402
from db.serializers import SimulationOutputSerializer
from datetime import time, date, datetime
import json


def test_basic_sim_with_models():
    """Basic test of sim with models"""

    test_date = datetime(2023, 9, 15)
    StationM.objects.all().filter(station_id="0").delete()
    StationM.objects.all().filter(station_id="-1").delete()
    StationM.objects.all().filter(station_id="-2").delete()
    CalendarM.objects.all().filter(service_id="0").delete()

    # make calender
    CalendarM.objects.get_or_create(
        service_id="0",
        monday=False,
        tuesday=False,
        wednesday=False,
        thursday=False,
        friday=True,
        saturday=False,
        sunday=False,
        start_date=test_date,
        end_date=test_date,
    )

    # make stations
    StationM.objects.get_or_create(
        station_id="0",
        station_code="0",
        name="first stop",
        lat=0,
        long=0,
        location_type=3,
        suburb="test suburb",
    )

    StationM.objects.get_or_create(
        station_id="-1",
        station_code="-1",
        name="middle stop",
        lat=2,
        long=2,
        location_type=3,
        suburb="test suburb",
    )

    StationM.objects.get_or_create(
        station_id="-2",
        station_code="-2",
        name="last stop",
        lat=4,
        long=4,
        location_type=3,
        suburb="test suburb",
    )

    # make route
    RouteM.objects.get_or_create(
        route_id="0", name="test", transport_type=3, capacity=50
    )

    # make shape
    ShapeM.objects.get_or_create(
        shape_id=0,
        shape_pt_lat=0,
        shape_pt_lon=0,
        shape_pt_sequence=0,
    )

    # make trip 1
    TripM.objects.get_or_create(
        trip_id=1,
        route_id=RouteM.objects.get(route_id=0),
        shape_id=ShapeM.objects.get(shape_id=0),
        service_id=CalendarM.objects.get(service_id=0),
    )

    # make timetable for trip 1
    TimetableM.objects.get_or_create(
        trip_id=TripM.objects.get(trip_id=1),
        station=StationM.objects.get(station_id=0),
        arrival_time=time(0, 10),
        sequence=1,
    )

    # make timetable for trip 1
    TimetableM.objects.get_or_create(
        trip_id=TripM.objects.get(trip_id=1),
        station=StationM.objects.get(station_id=-1),
        arrival_time=time(0, 20),
        sequence=2,
    )

    # make timetable for trip 1
    TimetableM.objects.get_or_create(
        trip_id=TripM.objects.get(trip_id=1),
        station=StationM.objects.get(station_id=-2),
        arrival_time=time(0, 30),
        sequence=3,
    )

    # make trip 2
    TripM.objects.get_or_create(
        trip_id=2,
        route_id=RouteM.objects.get(route_id=0),
        shape_id=ShapeM.objects.get(shape_id=0),
        service_id=CalendarM.objects.get(service_id=0),
    )

    # make timetable for trip 2
    TimetableM.objects.get_or_create(
        trip_id=TripM.objects.get(trip_id=2),
        station=StationM.objects.get(station_id=0),
        arrival_time=time(0, 0),
        sequence=1,
    )

    # make timetable for trip 2
    TimetableM.objects.get_or_create(
        trip_id=TripM.objects.get(trip_id=2),
        station=StationM.objects.get(station_id=-1),
        arrival_time=time(0, 10),
        sequence=2,
    )

    # make timetable for trip 2
    TimetableM.objects.get_or_create(
        trip_id=TripM.objects.get(trip_id=2),
        station=StationM.objects.get(station_id=-2),
        arrival_time=time(0, 20),
        sequence=3,
    )

    run_simulation(
        {
            "env_start": 0,
            "time_horizon": 30,
            "itineraries": [
                {
                    "itinerary_id": 0,
                    "routes": [{"route_id": "0", "start": "0", "end": "-2"}],
                },
                {
                    "itinerary_id": 1,
                    "routes": [
                        {"route_id": "walk", "start": "0", "end": "-1"},
                        {"route_id": "0", "start": "-1", "end": "-2"},
                    ],
                },
            ],
            "snapshot_date": "2023-09-15",
            "active_suburbs": ["test suburb"],
            "active_stations": ["0"],
        },
        2,
    )


def test_sim_with_db_models_412():
    run_simulation(
        {
            "env_start": 355,
            "time_horizon": 120,
            "itineraries": [
                {
                    "itinerary_id": 0,
                    "routes": [{"route_id": "412-3136", "start": "0", "end": "1850"},
                               {"route_id":"walk", "start":"1850", "end": "1846"}],
                }
            ],
            "snapshot_date": "2023-08-01",
            "active_suburbs": ["St Lucia"],
            "active_stations": ["1815"],
        },
        1,
    )


def test_sim_output_serializer():
    station = StationSim(
        station_id="0",
        name="test_station",
        lat=0,
        long=0,
        passenger_count=PassengerChanges(
            passenger_changes_id=0,
            time=0,
            passenger_count=0,
        ),
    )

    route = RouteSim(
        route_id="0",
        method="test_route",
        buses_on_route=BusOnRouteInfo(
            bus_id="0",
            bus_timeout=BusTimeOut(
                bustimeout_id=0,
                stop_name="0",
                time=0,
            ),
            bus_passenger_changes=PassengerChanges(
                passenger_changes_id=1,
                time=0,
                passenger_count=50,
            ),
        ),
        stations=station,
    )

    output = SimulationOutput(
        simulation_id=0,
        route_id=route,
        station_id=station,
        itinerary_id=ItinerarySim(
            itinerary_id="0",
            routes=route,
        ),
    )
    serializer = SimulationOutputSerializer(output)
    print(json.dumps(serializer.data))


if __name__ == "__main__":
    test_sim_with_db_models_412()
