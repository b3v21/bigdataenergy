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
)  # noqa: E402

from datetime import time, date, datetime


def simple_example(env_start: int) -> None:
    env = Environment()

    first_stop = Station(
        env=env,
        id=0,
        name="First Stop",
        pos=(0, 0),
        bays=1,
        env_start=env_start,
    )
    last_stop = Station(
        env=env,
        id=1,
        name="Last Stop",
        pos=(2, 2),
        bays=1,
        env_start=env_start,
    )
    stadium = Station(
        env=env,
        id=2,
        name="Stadium",
        pos=(4, 4),
        bays=1,
        env_start=env_start,
    )

    trip = Trip(
        timetable=[("First Stop", 0), ("Last Stop", 30)],
    )
    trip_2 = Trip(
        timetable=[("First Stop", 15), ("Last Stop", 45)],
    )
    trip_3 = Trip(
        timetable=[("First Stop", 30), ("Last Stop", 60)],
    )

    bus_route = BusRoute(
        env=env,
        env_start=env_start,
        id=0,
        name="R",
        stops=[first_stop, last_stop],
        trip_timing_data=[trip, trip_2, trip_3],
    )

    walk_to_stadium = Walk(
        id=10,
        env=env,
        env_start=env_start,
        stops=[last_stop, stadium],
    )

    itinerary1 = Itinerary(
        env=env, id=0, routes=[(bus_route, None), (walk_to_stadium, None)]
    )
    ITINERARIES.append(itinerary1)

    Suburb(
        env=env,
        name="Simple Suburb",
        station_distribution={first_stop: 100, last_stop: 0},
        population=100,
        frequency=10,
        max_distributes=0,
        itineraries=[itinerary1],
        env_start=env_start,
    )

    env.run(100)

    """
    Could this be done easier by have the arrays storing all objects of that being created 
    from the instruction method and then could be called as an object on the class?
    """
    stops = [
        first_stop,
        last_stop,
        stadium,
    ]  # Maybe have this setup on construct from method?
    station_out = {}
    for stop in stops:
        station_out[stop.id] = stop.people_over_time

    bus_routes = [bus_route]
    bus_route_time_out = {}
    bus_route_pop_out = {}
    for route in bus_routes:
        bus_route_time_out[route.id] = route.bus_time_log
        bus_route_pop_out[route.id] = route.bus_passenger_changes

    walk_routes = [walk_to_stadium]
    walk_route_out = {}
    for route in walk_routes:
        walk_route_out[route.id] = route.walk_time_log

    print()
    print(station_out)
    print()
    print(bus_route_time_out)
    print(bus_route_pop_out)
    print()
    print(walk_route_out)

    for stop in stops:
        print(f"{stop.id}: {stop.name}")
        for people in stop.people:
            print(people.people_log)


def complex_example(env_start: int) -> None:
    env = Environment()

    first_stop = Station(
        env=env,
        id=0,
        name="First Stop",
        pos=(0, 0),
        bays=1,
        env_start=env_start,
    )
    second_stop = Station(
        env=env,
        id=1,
        name="Second Stop",
        pos=(1, 1),
        bays=1,
        env_start=env_start,
    )
    last_stop = Station(
        env=env,
        id=2,
        name="Last Stop",
        pos=(2, 2),
        bays=1,
        env_start=env_start,
    )
    stadium = Station(
        env=env,
        id=3,
        name="Stadium",
        pos=(4, 4),
        bays=1,
        env_start=env_start,
    )

    X_trip = Trip(
        timetable=[("First Stop", 0), ("Last Stop", 30)],
    )

    X_trip_2 = Trip(
        timetable=[("First Stop", 30), ("Last Stop", 60)],
    )

    Y_trip = Trip(
        timetable=[("First Stop", 15), ("Second Stop", 30), ("Last Stop", 45)],
    )

    Z_trip = Trip(
        timetable=[("Second Stop", 0), ("Last Stop", 15), ("Stadium", 20)],
    )

    Z_trip_2 = Trip(
        timetable=[
            ("Second Stop", 45),
            ("Last Stop", 60),
            ("Stadium", 65),
        ],  # How do we handle route wrap over, or is this covered by the datetime
    )

    bus_route_X = BusRoute(
        env=env,
        env_start=env_start,
        id=0,
        name="X",
        stops=[first_stop, last_stop],
        trip_timing_data=[X_trip, X_trip_2],
    )

    bus_route_Y = BusRoute(
        env=env,
        env_start=env_start,
        id=1,
        name="Y",
        stops=[first_stop, second_stop, last_stop],
        trip_timing_data=[Y_trip],
    )

    bus_route_Z = BusRoute(
        env=env,
        env_start=env_start,
        id=2,
        name="Z",
        stops=[second_stop, last_stop, stadium],
        trip_timing_data=[Z_trip, Z_trip_2],
    )

    walk_to_stadium = Walk(
        id=10,
        env=env,
        env_start=env_start,
        stops=[last_stop, stadium],
    )

    itinerary1 = Itinerary(
        env=env, id=1, routes=[(bus_route_X, None), (walk_to_stadium, None)]
    )
    itinerary2 = Itinerary(
        env=env, id=2, routes=[(bus_route_Y, None), (walk_to_stadium, None)]
    )
    itinerary3 = Itinerary(
        env=env, id=3, routes=[(bus_route_Z, last_stop), (walk_to_stadium, None)]
    )
    itinerary4 = Itinerary(env=env, id=4, routes=[(bus_route_Z, None)])
    ITINERARIES.append(itinerary1)
    ITINERARIES.append(itinerary2)
    ITINERARIES.append(itinerary3)
    ITINERARIES.append(itinerary3)

    Suburb(
        env=env,
        name="Simple Suburb",
        station_distribution={first_stop: 50, second_stop: 40, last_stop: 10},
        population=200,
        frequency=10,
        max_distributes=3,
        itineraries=[itinerary1, itinerary2, itinerary3, itinerary4],
        env_start=env_start,
    )

    env.run(125)

    stops = [
        first_stop,
        second_stop,
        last_stop,
        stadium,
    ]  # Maybe have this setup on construct from method?
    station_out = {}
    for stop in stops:
        station_out[stop.id] = stop.people_over_time

    bus_routes = [bus_route_Z]
    bus_route_time_out = {}
    bus_route_pop_out = {}
    for route in bus_routes:
        bus_route_time_out[route.id] = route.bus_time_log
        bus_route_pop_out[route.id] = route.bus_passenger_changes

    walk_routes = [walk_to_stadium]
    walk_route_out = {}
    for route in walk_routes:
        walk_route_out[route.id] = route.walk_time_log

    print()
    print(station_out)
    print()
    print(bus_route_time_out)
    print(bus_route_pop_out)
    print()
    print(walk_route_out)

    print()

    for stop in stops:
        print(f"{stop.id}: {stop.name}")
        for people in stop.people:
            if stop.name == "Stadium":
                print(people.get_num_people(), people.people_log)
            else:
                print(
                    people.get_num_people(),
                    people.people_log,
                    ITINERARIES[people.itinerary_index].get_current_route(people).name,
                )
                print(people)
                print(people.current_route_in_itin_index)

        print()


def test_efficiency():
    print()
    i = 0
    while i < 1:
        complex_example(0)
        i += 1



def test_sim_with_db_models_412():
    run_simulation(
        {
            "env_start": 355,
            "time_horizon": 30,
            "itineraries": {0: [{"route_id": "412-3136", "start": "0", "end": "1850"}]},
            "snapshot_date": datetime.strptime("2023-08-01", "%Y-%m-%d").date(),
        },
        1,
    )


if __name__ == "__main__":
    test_sim_with_db_models_412()
    # test_efficiency()
