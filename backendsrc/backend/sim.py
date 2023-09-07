from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from simpy import Environment, Resource
from collections import namedtuple
from random import randint
from pathlib import Path
from math import ceil
import django
import os
import sys

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


class Itinerary:
    """
    Object to store multiple types of travel at a time.
    """

    def __init__(self, env: Environment, id: int, routes: list[Route]):
        self.env = env
        self.routes = routes
        self.id = id
        self.index = 0

    def __str__(self):
        return f"Itinerary: ID: {self.id}, Routes: {self.routes}, Index: {self.index}"

    def get_current_type(self) -> str:
        return self.routes[self.index].get_type()

    def get_current_route(self) -> Route:
        return self.routes[self.index]

    def next(self) -> None:
        self.index += 1

    def last_leg(self) -> bool:
        return self.index == len(self.routes)

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
        itinerary: Itinerary,
        env_start: int,
    ) -> None:
        self.env_start = start_time
        self.env = env
        self.num_people = count
        self.start_time = start_time
        self.start_location = start_location
        self.end_time = None
        self.itinerary = itinerary
        self.travel_route = None  # To come later

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
        route_stops = self.itinerary.get_current_route().stops
        return route_stops[(route_stops.index(current_stop) + 1) % len(route_stops)]


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
        bus_timings: dict[str, list[int]],
        bus_spawn_max: int = 0,
    ) -> None:
        self.env_start = env_start
        self.env = env
        self.id = id
        self.name = name
        self.pos = pos
        self.bays = Resource(env, capacity=bays)
        self.people = []
        self.bus_timings = bus_timings
        self.bus_spawn_max = bus_spawn_max
        self.buses_spawned = 0

    def __str__(self) -> str:
        output = f"{self.name}: Total People = {self.num_people()}, Total Groups = {len(self.people)}"
        for people in self.people:
            output += f"\n{str(people)}"
        return output

    # For adding more groups of people to stops (if more rock up at a different time)

    def add_people(self, new_people: People) -> None:
        self.people.append(new_people)

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
                    people.itinerary.duplicate(),
                    self.env_start,
                )
                split.itinerary.index = people.itinerary.index
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

        return people_to_get

    def put(self, passengers: list[People], from_suburb=False) -> None:
        for p in passengers:
            if not from_suburb and not p.itinerary.last_leg():
                p.itinerary.next()
            if p.itinerary.last_leg():
                # Being put at end
                self.people.append(p)
            elif p.itinerary.get_current_type() == "BusRoute":
                self.people.append(p)
            elif p.itinerary.get_current_type() == "Walk":
                # Queue people all up to walk
                self.env.process(
                    Walk(
                        env=self.env,
                        env_start=self.env_start,
                        stops=[self, p.get_next_stop_current_route(self)],
                        people=[p],
                    ).initiate_route()
                )

    def num_people(self) -> int:
        return sum([people.get_num_people() for people in self.people])

    def get_bus_timings(self) -> list[int]:
        return self.bus_timings


class Transporter(ABC):
    """Abstract transporter object"""

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        location_index: int = 0,
        people: list[People] = [],
        capacity: int = 50
    ) -> None:
        self.env = env
        self.env_start = env_start
        self.id = id
        self.location_index = location_index
        self.people = people
        self.capacity = capacity

    def get_name(self) -> str:
        return f"B{self.id}"
    
    def load_passengers(self, station : Station) -> None:
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

        print(
            f"({self.env.now+self.env_start}): {self.get_type()} {self.get_name()} loaded {num_people_to_board} people from {station.name} ({load_time} mins)"
        )

    def deload_passengers(self, station: Station) -> None:
        # Currently all passengers get off...
        get_off = self.passenger_count()

        if not get_off:
            print(
                f"({self.env.now+self.env_start}): No passengers got off the bus {self.get_name()}"
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
        location_index: int = 0,
        people: list[People] = [],
        capacity: int = 50,
    ) -> None:
        super().__init__(env, env_start, id, location_index, people, capacity)
        
    def get_type(self) -> str:
        return "Bus"
        

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
    ) -> None:
        self.id = id
        self.name = name
        self.stops = stops
        self.first_stop = stops[0]
        self.last_stop = stops[-1]
        self.env = env
        self.env_start = env_start

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
    ) -> None:
        super().__init__(env, env_start, id, name, stops)
        self.running = self.env.process(self.initiate_route())
        self.buses: list[Bus] = []

    def initiate_route(self) -> None:
        """
        A function to initiate the route. Will spawn busses on the according time
        intervals and then handle how these buses transport people along the route
        """

        while True:
            if (self.first_stop.buses_spawned != self.first_stop.bus_spawn_max) and (
                self.env.now in self.first_stop.bus_timings.get(self.name)
            ):
                new_bus = Bus(
                    env=self.env,
                    env_start=self.env_start,
                    id=self.first_stop.buses_spawned,
                )
                self.first_stop.buses_spawned += 1
                self.add_bus(new_bus)
                print(
                    f"({self.env.now+self.env_start}): Bus {new_bus.get_name()} started on route {self.name}"
                )
                yield self.env.timeout(1)

            for bus in self.buses:
                with self.get_current_stop(bus).bays.request() as req:
                    yield req
                    if self.get_current_stop(bus) != self.last_stop:
                        yield self.env.process(
                            bus.load_passengers(self.get_current_stop(bus))
                        )
                    else:
                        yield self.env.process(
                            bus.deload_passengers(self.get_current_stop(bus))
                        )

                    previous_stop = self.stops[bus.location_index]
                    bus.move_to_next_stop(len(self.stops))

                stop_times = self.stops[bus.location_index].bus_timings.get(self.name)

                next_stop_times = [
                    x for x in stop_times if x > int(self.env.now + self.env_start) % 60
                ]
                if not next_stop_times:
                    travel_time = (
                        60 - int(self.env.now + self.env_start) % 60 + stop_times[0]
                    )
                else:
                    travel_time = (
                        next_stop_times[0] - int(self.env.now + self.env_start) % 60
                    )
                yield self.env.timeout(travel_time)
                print(
                    f"({self.env.now+self.env_start}): Bus {self.name} travelled from {previous_stop.name} to {self.get_current_stop(bus).name} ({travel_time} mins)"
                )

    def get_type(self) -> str:
        return "BusRoute"

    def add_bus(self, new_bus: Bus) -> None:
        self.buses.append(new_bus)

    def get_current_stop(self, bus: Bus) -> Station:
        return self.stops[bus.location_index]


class Walk(Route):
    """A group of people walking through a route"""

    def __init__(
        self,
        env: Environment,
        env_start: int,
        stops: list[Station],
        location_index: int = 0,
        people: list[People] = [],
    ) -> None:
        super().__init__(env, env_start, None, None, stops)
        self.walking_congestion = 1
        self.location_index = location_index
        self.people = people

    def initiate_route(self) -> None:
        """
        Walking process
        """

        walk_time = self.walk_time() * self.walking_congestion
        yield self.env.timeout(walk_time)
        self.stops[1].put(self.people)
        print(
            f"({self.env_start+self.env.now}): {self.get_num_people()} people walked from {self.stops[0].name} to {self.stops[1].name} ({walk_time} mins)"
        )

    def get_num_people(self) -> int:
        return sum(group.get_num_people() for group in self.people)

    def walk_time(self) -> int:
        """
        Reponsible for calculating the walk time between two locations (use google maps api)
        """
        return randint(5, 20)

    def get_type(self) -> str:
        return "Walking"


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

            # this triple for loop is definately bad but will probably get updated
            # when further refactoring occurs.
            for itinerary in self.itineraries:
                for route in itinerary.routes:
                    for route_stop in route.stops:
                        if route_stop == stop:
                            valid_itinerary_for_people = itinerary

            people_arriving_at_stop = People(
                env=self.env,
                count=num_for_stop,
                start_time=self.env.now,
                start_location=stop,
                itinerary=valid_itinerary_for_people,
                env_start=self.env_start,
            )
            stop.put([people_arriving_at_stop], from_suburb=True)

            print(
                f"({self.env.now+self.env_start}): {num_for_stop} people arrived at {stop.name} in {self.name}"
            )

            have_distributed += num_for_stop
            return have_distributed


def simple_example(
    env: Environment, env_start: int, data: tuple(list[Station], list[Route])
) -> None:
    first_stop = Station(
        env=env,
        id=0,
        name="first_stop",
        pos=(0, 0),
        bays=1,
        env_start=env_start,
        bus_timings={"the_route": list(range(0, 60, 5))},
        bus_spawn_max=1,
    )
    last_stop = Station(
        env=env,
        id=1,
        name="last_stop",
        pos=(2, 2),
        bays=1,
        env_start=env_start,
        bus_timings={"the_route": list(range(0, 60, 5))},
    )
    stadium = Station(
        env=env,
        id=2,
        name="stadium",
        pos=(4, 4),
        bays=1,
        env_start=env_start,
        bus_timings={"the_route": list(range(0, 60, 5))},
    )

    bus_route = BusRoute(
        env=env,
        env_start=env_start,
        id=0,
        name="the_route",
        stops=[first_stop, last_stop],
    )
    walk_to_stadium = Walk(
        env=env,
        env_start=env_start,
        stops=[last_stop, stadium],
    )

    itinerary = Itinerary(env=env, id=0, routes=[bus_route, walk_to_stadium])

    Suburb(
        env=env,
        name="Simple Suburb",
        station_distribution={first_stop: 100, last_stop: 0},
        population=100,
        frequency=10,
        max_distributes=0,
        itineraries=[itinerary],
        env_start=env_start,
    )

    env.run(50)


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

    station_objects = {}
    route_objects = {}

    return (station_objects, route_objects)


if __name__ == "__main__":
    env = Environment()
    print()
    simple_example(env, START_TIME, get_data(env, env_start=START_TIME))
    print()
