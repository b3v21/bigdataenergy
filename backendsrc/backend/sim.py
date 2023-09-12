from __future__ import annotations
from simpy import Environment, Resource
from abc import ABC, abstractmethod
from random import randint, randrange
from pathlib import Path
from math import ceil, floor
import django
import os
import sys
import copy

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from db.models import (
    Station as StationM,
    Route as RouteM,
    Timetable as TimetableM,
)  # noqa: E402


START_TIME = 12
PERSON_BOARD_TIME = 0.1
MINUTES_IN_DAY = 1440

ITINERARIES = []


class Itinerary:
    """
    Object to store multiple types of travel at a time.
    """

    def __init__(self, env: Environment, id: int, routes: list[Route]):
        self.env = env
        self.routes = routes
        self.id = id

    def __str__(self):
        return f"Itinerary: ID: {self.id}, Routes: {self.routes}"

    def get_current_type(self, people: People) -> str:
        return self.routes[people.current_route_in_itin_index].get_type()

    def get_current(self, people: People) -> Route:
        return self.routes[people.current_route_in_itin_index]

    def last_leg(self, people: People) -> bool:
        return people.current_route_in_itin_index == len(self.routes)

    def duplicate(self, suburb=False):
        new = Itinerary(self.env, self.id, self.routes)
        if not suburb:
            new.index = self.index
        new.id += 1
        return new


class People:
    """
    A group of people which will travel along a route.
    """

    def __init__(
        self,
        env: Environment,
        count: int,
        start_time: int,
        start_location: Station,
        itinerary_index: int,
        env_start: int,
        current_route_in_itin_index: int = 0,
    ) -> None:
        self.env_start = env_start
        self.env = env
        self.num_people = count
        self.start_time = start_time
        self.start_location = start_location
        self.end_time = None
        self.itinerary_index = itinerary_index
        self.current_route_in_itin_index = (
            current_route_in_itin_index  # route index within an itinerary
        )
        self.people_log = {}
        self.expected_end_time = None  # How could we come up with this?

    def log(self, where: tuple(str, int)) -> None:
        self.people_log[self.env.now + self.env_start] = where

    def __str__(self) -> str:
        journey_time = (
            self.get_end_time() - self.get_start_time()
            if self.get_end_time() != None
            else "N/A"
        )

        return f"Count: {self.get_num_people()}, Start Time: {self.get_start_time()}, End Time: {self.get_end_time()}, Journey Time: {journey_time}, Start Loc: {self.start_location.name}"

    def get_num_people(self) -> int:
        return self.num_people

    def add_start_loc(self, location: Station) -> None:
        self.start_location = location

    def change_num_people(self, change: int) -> None:
        self.num_people += change

    def get_start_time(self) -> float:
        return self.start_time

    def set_end_time(self, time: float) -> None:
        self.end_time = time

    def get_end_time(self) -> float:
        return self.end_time

    def get_next_stop_current_route(self, current_stop: Station) -> list[Station]:
        route_stops = (
            ITINERARIES[self.itinerary_index]
            .routes[self.current_route_in_itin_index]
            .stops
        )
        return route_stops[(route_stops.index(current_stop) + 1) % len(route_stops)]

    def next_route(self) -> None:
        self.current_route_in_itin_index += 1


class Station:
    """
    Each Station object contains a SimPy Resource which represents the number of bus
    bays available at the stop. Also a list of People objects representing the people
    waiting at the bus stop is stored.
    """

    def __init__(
        self,
        env: Environment,
        id: int,
        name: str,
        pos: tuple[int, int],
        bays: int,
        env_start: int,
    ) -> None:
        self.env_start = env_start
        self.env = env
        self.id = id
        self.name = name
        self.pos = pos
        self.bays = Resource(env, capacity=bays)
        self.people = []
        self.people_over_time = {}

    def log_cur_people(self, num_people=None) -> None:
        if num_people:
            self.people_over_time[self.env.now + self.env_start] = num_people
        else:
            self.people_over_time[self.env.now + self.env_start] = self.num_people()

    def __str__(self) -> str:
        output = f"{self.name}: Total People = {self.num_people()}, Total Groups = {len(self.people)}"
        for people in self.people:
            output += f"\n{str(people)}"
        return output

    def board(self, num_people_to_board: int) -> list[People]:
        """
        Given the number of people who are at the stop, this method returns a list
        'people_to_get' containing the people which a bus can collect from this stop.
        """
        cur_total = 0
        people_to_get = []

        for people in self.people:
            if people.get_num_people() + cur_total > num_people_to_board:
                # Would be adding too many people --> Split
                excess = (people.get_num_people() + cur_total) - num_people_to_board
                split = People(
                    self.env,
                    excess,
                    people.start_time,
                    people.start_location,
                    people.itinerary_index,
                    self.env_start,
                    people.current_route_in_itin_index,
                )
                split.people_log = copy.deepcopy(people.people_log)
                people.change_num_people(-excess)
                self.people.append(split)
                people_to_get.append(people)
                self.people.remove(people)
                break
            people_to_get.append(people)
            self.people.remove(people)
            cur_total += people.get_num_people()
            if cur_total == num_people_to_board:
                break

        self.log_cur_people(self.num_people())
        return people_to_get

    def put(self, passengers: list[People], from_suburb=False) -> None:
        count = 0
        count_pre_add = (
            self.num_people()
        )  # Doing it this way as some transport doesnt log them in the station
        for group in passengers:
            group.log((self.name, self.id))
            count += group.get_num_people()
            if not from_suburb and not ITINERARIES[group.itinerary_index].last_leg(
                group
            ):
                group.next_route()
            if ITINERARIES[group.itinerary_index].last_leg(group):
                self.people.append(group)
            elif (
                ITINERARIES[group.itinerary_index].get_current_type(group) == "BusRoute"
            ):
                self.people.append(group)

            elif ITINERARIES[group.itinerary_index].get_current_type(group) == "Walk":
                # Queue people all up to walk
                time_to_wait = 0.5
                self.env.process(
                    ITINERARIES[group.itinerary_index]
                    .get_current(group)
                    .walk_instance(group, time_to_wait)
                )

        self.log_cur_people(count_pre_add + count)

    def num_people(self) -> int:
        return sum([people.get_num_people() for people in self.people])


class Transporter(ABC):
    """Abstract transporter object"""

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        name: str,
        trip: Trip,  # key = order, value = (Station, Time)
        location_index: int = 0,
        people: list[People] = [],
        capacity: int = 50,
    ) -> None:
        self.env = env
        self.env_start = env_start
        self.id = id
        self.name = name
        self.location_index = location_index
        self.people = people
        self.capacity = capacity
        self.trip = trip

    def get_name(self) -> str:
        return f"{self.name}"

    def load_passengers(self, station: Station) -> None:
        """Load passengers from the current stop onto this transporter."""

        seats_left = self.capacity - self.passenger_count()
        people_at_stop = sum(group.get_num_people() for group in station.people)

        if not people_at_stop:
            print(
                f"({self.env.now+self.env_start}): No passengers at stop {station.name}"
            )
            return

        if not seats_left:
            print(
                f"({self.env.now+self.env_start}): No seats left on bus {self.get_name()}"
            )
            return

        people_to_ride = station.board(min(people_at_stop, seats_left))

        num_people_to_board = sum([p.get_num_people() for p in people_to_ride])
        load_time = int(num_people_to_board * PERSON_BOARD_TIME)
        self.people += people_to_ride

        yield self.env.timeout(load_time)
        for people in people_to_ride:
            people.log((self.name, self.id))
        print(
            f"({self.env.now+self.env_start}): {self.get_type()} {self.get_name()} loaded {num_people_to_board} people from {station.name} ({load_time} mins)"
        )

    def deload_passengers(self, station: Station) -> None:
        # Currently all passengers get off...
        get_off = self.passenger_count()

        if not get_off:
            print(
                f"({self.env.now+self.env_start}): No passengers got off {self.get_type()}: {self.get_name()}"
            )
            return

        off_time = int(get_off * PERSON_BOARD_TIME)
        yield self.env.timeout(off_time)
        print(
            f"({self.env.now+self.env_start}): {self.get_type()} {self.get_name()} has dropped off {get_off} people at {station.name} ({off_time} mins)"
        )

        station.put(self.people)
        self.people.clear()

    def move_to_next_stop(self, num_stops: int) -> None:
        new_location_index = (self.location_index + 1) % num_stops
        self.location_index = new_location_index

    def passenger_count(self) -> int:
        return sum(group.get_num_people() for group in self.people)

    @abstractmethod
    def get_type(self) -> str:
        pass


class Bus(Transporter):
    """A bus moving through a route"""

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        name: str,
        trip: Trip,
        location_index: int = 0,
        people: list[People] = [],
        capacity: int = 50,
    ) -> None:
        super().__init__(
            env, env_start, id, name, trip, location_index, people, capacity
        )
        self.bus_pop_log = {}

    def get_type(self) -> str:
        return "Bus"

    def __str__(self) -> str:
        return f"{self.id}, {self.trip}, {self.location_index}, {self.people}, {self.capacity}"

    def bus_instance(self, bus_route: BusRoute) -> None:
        bus_route.bus_pop_log[self.id] = {}
        while True:
            with bus_route.get_current_stop(self).bays.request() as req:
                yield req
                print(
                    f"({self.env.now+bus_route.env_start}): Bus {self.get_name()} arrived at {bus_route.get_current_stop(self).name}"
                )
                bus_route.bus_time_log[self.id][
                    bus_route.get_current_stop(self).name
                ] = (self.env.now + self.env_start)
                if bus_route.get_current_stop(self) != bus_route.last_stop:
                    yield self.env.process(
                        self.load_passengers(bus_route.get_current_stop(self))
                    )
                    bus_route.bus_pop_log[self.id][
                        self.env.now + self.env_start
                    ] = self.passenger_count()
                else:
                    yield self.env.process(
                        self.deload_passengers(bus_route.get_current_stop(self))
                    )
                    bus_route.bus_pop_log[self.id][
                        self.env.now + self.env_start
                    ] = self.passenger_count()
                    # Despawn
                    print(
                        f"({self.env.now+bus_route.env_start}): Bus {self.get_name()} ended its journey."
                    )
                    break

                previous_stop = bus_route.stops[self.location_index]
                self.move_to_next_stop(len(bus_route.stops))

                stop_times = [t[1] for t in self.trip.timetable]

                next_stop_times = [
                    x
                    for x in stop_times
                    if x > int(self.env.now + bus_route.env_start) % 60
                ]
                if not next_stop_times:
                    travel_time = (
                        60
                        - int(self.env.now + bus_route.env_start) % 60
                        + stop_times[0]
                    )
                else:
                    travel_time = (
                        next_stop_times[0]
                        - int(self.env.now + bus_route.env_start) % 60
                    )
            yield self.env.timeout(travel_time)
            bus_route.bus_time_log[self.id][bus_route.get_current_stop(self).name] = (
                self.env.now + self.env_start
            )
            print(
                f"({self.env.now+bus_route.env_start}): Bus {self.get_name()} travelled from {previous_stop.name} to {bus_route.get_current_stop(self).name} ({travel_time} mins)"
            )


class Route(ABC):
    """
    Object to store series of routes, needs to spawn the initial stops bus spawn process.
    """

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        name: str,
        stops: list[Station],
        trip_timing_data: list[Trip],
        transporter_spawn_max: int = 1,
    ) -> None:
        self.id = id
        self.name = name
        self.stops = stops
        self.first_stop = stops[0]
        self.last_stop = stops[-1]
        self.env = env
        self.env_start = env_start
        self.transporter_spawn_max = transporter_spawn_max
        self.trip_timing_data = trip_timing_data
        self.transporters_spawned = 0

    def get_stations(self):
        return self.stops

    @abstractmethod
    def initiate_route(self) -> None:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass


class BusRoute(Route):
    """
    A route of buses. Buses arrive at the bus stop for picking up people.

    The bus then requests one of the bus stops stops pumps and tries to get the
    desired amount of people from it.
    """

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        name: str,
        stops: list[Station],
        trip_timing_data: list[Trip],
        transporter_spawn_max: int = 3,
    ) -> None:
        super().__init__(
            env, env_start, id, name, stops, trip_timing_data, transporter_spawn_max
        )
        self.running = self.env.process(self.initiate_route())
        self.buses: list[Bus] = []
        self.bus_time_log = []
        self.bus_pop_log = {}  # {id : bus_pop_log}

    def initiate_route(self) -> None:
        """
        A function to initiate the route. Will spawn busses on the according time
        intervals and then handle how these buses transport people along the route
        """

        trips_to_iniate = self.trip_timing_data
        while True:
            if self.transporters_spawned != self.transporter_spawn_max:
                # get the location of the bus to spawn if the current time exists in
                # the timetable.
                stop_info = None
                trip_info = None
                trips_inited = []
                for trip in trips_to_iniate:
                    for stop in trip.timetable:
                        if stop[1] == (self.env.now + self.env_start):
                            stop_info = stop
                            trip_info = trip
                            # Now have a trip to start
                            new_bus = Bus(
                                env=self.env,
                                env_start=self.env_start,
                                id=self.transporters_spawned,
                                name=f"B{self.transporters_spawned}_{self.name}",
                                trip=trip_info,
                                location_index=self.get_stop_with_name(stop_info[0]),
                                people=[],
                            )
                            self.transporters_spawned += 1
                            self.add_bus(new_bus)
                            self.env.process(new_bus.bus_instance(self))
                            self.bus_time_log.append({})
                            print(
                                f"({self.env.now+self.env_start}): Bus {new_bus.get_name()} started on route {self.name}"
                            )
                            trips_inited.append(trip)
                for trip in trips_inited:
                    trips_to_iniate.remove(trip)
            else:
                break
            yield self.env.timeout(1)

    def get_type(self) -> str:
        return "BusRoute"

    def add_bus(self, new_bus: Bus) -> None:
        self.buses.append(new_bus)

    def get_current_stop(self, bus: Bus) -> Station:
        return self.stops[bus.location_index]

    def get_stop_with_name(self, name: str) -> Station:
        return [stop.name for stop in self.stops].index(name)


class Walk(Route):
    """A group of people walking through a route"""

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        stops: list[Station],
        location_index: int = 0,
        people: list[People] = [],
    ) -> None:
        super().__init__(env, env_start, id, None, stops, None, None)
        self.walking_congestion = 1
        self.location_index = location_index
        self.people = people
        self.walk_time_log = {}

    def initiate_route(self) -> None:
        return super().initiate_route()

    def walk_instance(self, people: People, time_to_leave=0) -> None:
        """
        Walking process
        """
        yield self.env.timeout(time_to_leave)
        people.log((self.stops, self.id))
        self.walk_time_log[people] = [
            self.env.now + self.env_start,
            None,
        ]  # Maybe change this to be an ID
        self.people.append(people)
        self.stops[0].log_cur_people()
        walk_time = self.walk_time() * self.walking_congestion
        yield self.env.timeout(walk_time)
        self.people.remove(people)
        self.walk_time_log[people][1] = self.env.now + self.env_start
        self.stops[1].put([people])
        print(
            f"({self.env_start+self.env.now}): {people.get_num_people()} people walked from {self.stops[0].name} to {self.stops[1].name} ({walk_time} mins)"
        )

    def get_num_people(self) -> int:
        return sum(group.get_num_people() for group in self.people)

    def walk_time(self) -> int:
        """
        Reponsible for calculating the walk time between two locations (use google maps api)
        """
        return randint(5, 20)

    def get_type(self) -> str:
        return "Walk"


class Suburb:
    def __init__(
        self,
        env: Environment,
        name: str,
        station_distribution: dict[Station, float],
        population: int,
        frequency: int,
        max_distributes: int,
        itineraries: list[Itinerary],
        env_start: int,
    ) -> None:
        self.env = env
        self.env_start = env_start
        self.name = name
        self.station_distribution = station_distribution
        self.population = population
        self.frequency = frequency  # How often to try and distribute the population
        self.max_distributes = max_distributes
        self.itineraries = itineraries

        # Start process
        self.pop_proc = self.env.process(self.suburb())

    def suburb(self) -> None:
        """
        Every frequency minutes, will distribute random amount of population to nearby
        stations.
        """
        current_distribution = 0

        while current_distribution < self.max_distributes:
            if self.env.now % self.frequency == 0:
                num_people = randint(0, self.population)
                have_distributed = self.distribute_people(num_people)

            current_distribution += 1
            self.population -= have_distributed
            yield self.env.timeout(1)

        # distribute remaining people if there are any
        if self.population > 0:
            _ = self.distribute_people(self.population)

    def distribute_people(self, num_people: int) -> int:
        """
        Function which distributes people throughout a suburb. Returns the number
        of people distributed.
        """

        have_distributed = 0

        for stop in self.station_distribution.keys():
            if stop == list(self.station_distribution.keys())[-1]:
                num_for_stop = have_distributed
            else:
                num_for_stop = ceil(self.station_distribution[stop] / 100 * num_people)

            # Get a random valid itinerary (must include stop)
            valid_itinerary_for_people = None
            valid_stop_index = None

            # this triple for loop is definately bad but will probably get updated
            # when further refactoring occurs.
            for itinerary_index, itinerary in enumerate(ITINERARIES):
                for route in itinerary.routes:
                    for stop_index, route_stop in enumerate(route.stops):
                        if route_stop == stop:
                            valid_itinerary_for_people = itinerary_index
                            valid_stop_index = stop_index

            people_arriving_at_stop = People(
                env=self.env,
                count=num_for_stop,
                start_time=self.env.now,
                start_location=stop,
                itinerary_index=valid_itinerary_for_people,
                current_route_in_itin_index=valid_stop_index,
                env_start=self.env_start,
            )
            stop.put([people_arriving_at_stop], from_suburb=True)

            print(
                f"({self.env.now+self.env_start}): {num_for_stop} people arrived at {stop.name} in {self.name}"
            )

            have_distributed += num_for_stop
            return have_distributed


class Trip:
    """This trip object will be created to hold transporter timings"""

    def __init__(
        self, start_time: int, end_time: int, timetable: list[tuple[str, int]]
    ) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.timetable = timetable


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

    timetable_stops = ["First Stop", "Last Stop"]

    trip = Trip(
        start_time=0,
        end_time=50,
        timetable=[("First Stop", 0), ("Last Stop", 30)],
    )
    trip_2 = Trip(
        start_time=0,
        end_time=50,
        timetable=[("First Stop", 15), ("Last Stop", 45)],
    )
    trip_3 = Trip(
        start_time=0,
        end_time=50,
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

    itinerary1 = Itinerary(env=env, id=0, routes=[bus_route, walk_to_stadium])
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
        bus_route_pop_out[route.id] = route.bus_pop_log

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


def get_data(
    env: Environment, env_start: int = 0
) -> tuple[dict[int, Station], dict[int, Route]]:
    """
    This function accesses the data from the database and converts it into simulation
    objects.
    """

    stations = StationM.objects.all()
    routes = RouteM.objects.all()
    timetables = TimetableM.objects.all()

    # User inputs time window for simulation. For each route in the simulation, all trips
    # which lie inside the time window are obtained and saved in a list.

    station_objects = {}
    route_objects = {}

    return (station_objects, route_objects)


"""
Track a bunch info for each group of people.

In general track how many people are using a transporter at a time between stations.

Also change it so the end has ID from object to referncing summary stats.
"""


if __name__ == "__main__":
    print()
    simple_example(START_TIME)
    print()
