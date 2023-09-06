from __future__ import annotations
from simpy import Environment, Resource
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
        return self.routes[self.index].transport_type

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


class Walking:
    """
    Class for holding a 'block' of walking
    I Imagine down the line all the calculations in here will be done by Google Maps API

    I feel like this could be done in several ways but for now I'm thinking we create
    instances of the 'walking' class which can be assigned groups of people, then SOMEHOW
    down the line we can gather a walking congestion coefficient if multiple instances of
    walking that are within a certain proximity and pass some quantity threshold occur...
    """

    WALKING_CONGESTION = 1  # Temp

    def __init__(
        self,
        env: Environment,
        start_pos: tuple[int, int] | Station,  # Think about this later
        end_pos: tuple[int, int] | Station,
        people: list[People],
        env_start: int,
    ) -> None:
        self.env = env
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.people = people
        self.env_start = env_start

    def walk(self) -> None:
        """
        Walking process
        """

        walk_time = self.walk_time() * Walking.WALKING_CONGESTION
        yield self.env.timeout(walk_time)
        self.end_pos.put(self.people)
        print(
            f"({self.env_start+self.env.now}): {self.get_num_people()} people walked from {self.start_pos.name} to {self.end_pos.name} ({walk_time} mins)"
        )

    def get_num_people(self) -> int:
        return sum(group.get_num_people() for group in self.people)

    def walk_time(self) -> int:
        """
        Reponsible for calculating the walk time between two locations (use google maps api)
        """
        return randint(5, 20)


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
            elif p.itinerary.get_current_type() == "Bus":
                self.people.append(p)
            elif p.itinerary.get_current_type() == "Walking":
                # Queue people all up to walk
                self.env.process(
                    Walking(
                        self.env,
                        self,
                        p.itinerary.get_current_route().last_stop,
                        [p],
                        self.env_start,
                    ).walk()
                )

    def num_people(self) -> int:
        return sum([people.get_num_people() for people in self.people])

    def get_bus_timings(self) -> list[int]:
        return self.bus_timings


class Route:
    """
    Object to store series of routes, needs to spawn the initial stops bus spawn process.
    """

    def __init__(
        self,
        env: Environment,
        name: str,
        transport_type: str,
        stops: list[Station],
        env_start: int,
    ) -> None:
        self.name = name
        self.stops = stops
        self.transport_type = transport_type
        self.first_stop = stops[0]
        self.last_stop = stops[-1]
        self.env = env
        self.env_start = env_start

        if self.transport_type == "Bus":
            self.running = self.env.process(self.initiate_bus_route())

    def initiate_bus_route(self) -> None:
        """
        A function to initiate the route. Will spawn busses on the according time
        intervals.
        """

        while self.first_stop.buses_spawned != self.first_stop.bus_spawn_max:
            if self.env.now in self.first_stop.bus_timings.get(self.name):
                self.first_stop.buses_spawned += 1
                name = f"B{self.first_stop.buses_spawned}_{self.name}"
                self.env.process(
                    Bus(self.env, name, self, self.env_start).start_driving()
                )
                print(
                    f"({self.env.now+self.env_start}): Bus {name} started on route {self.name}"
                )
            yield self.env.timeout(1)

    def get_stations(self):
        return self.stops


class Bus:
    """
    A bus arrives at the bus stop for picking up people.

    It requests one of the bus stops stops pumps and tries to get the
    desired amount of people from it.

    If the stop is emptied, it will leave.
    """

    def __init__(
        self,
        env: Environment,
        name: str,
        route: Route,
        env_start: str,
        location_index: int = 0,
        capacity: int = 50,
    ) -> None:
        self.env_start = env_start
        self.passengers = []  # Container for passengers on it
        self.name = name
        self.route = route
        self.capacity = capacity
        self.env = env
        self.location_index = location_index

    def get_current_stop(self) -> str:
        return self.route.stops[self.location_index].name

    def start_driving(self) -> None:
        """
        Logic of a bus:
        When spawned --> Pick up people from current stop
        When full OR no more people --> Go to final stop OR go to next stop
        Repeat

        """
        while True:
            with self.route.stops[self.location_index].bays.request() as req:
                yield req
                if self.route.stops[(self.location_index)] != self.route.last_stop:
                    yield self.env.process(self.load_passengers())
                else:
                    yield self.env.process(self.deload_passengers())

                next = (self.location_index + 1) % len(self.route.stops)

            stop_times = self.route.stops[
                (self.location_index + 1) % len(self.route.stops)
            ].bus_timings.get(self.route.name)

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
            self.update_current_stop()
            yield self.env.timeout(travel_time)
            print(
                f"({self.env.now+self.env_start}): Bus {self.name} travelled from {self.get_current_stop()} to {self.route.stops[next].name} ({travel_time} mins)"
            )
            self.location_index = next

    def update_current_stop(self) -> None:
        self.current_stop = self.route.stops[self.location_index].name

    def load_passengers(self) -> None:
        """Load passengers from the current stop onto this bus."""

        bus_seats_left = self.capacity - self.passenger_count()
        people_at_stop = sum(
            group.get_num_people()
            for group in self.route.stops[self.location_index].people
        )

        if not people_at_stop:
            print(f"({self.env.now+self.env_start}): No passengers at stop {self.name}")
            return

        if not bus_seats_left:
            print(f"({self.env.now+self.env_start}): No seats left on bus {self.name}")
            return

        people_to_ride = self.route.stops[self.location_index].board(
            min(people_at_stop, bus_seats_left)
        )

        num_people_to_board = sum([p.get_num_people() for p in people_to_ride])
        load_time = int(num_people_to_board * PERSON_BOARD_TIME)
        self.passengers += people_to_ride

        yield self.env.timeout(load_time)

        print(
            f"({self.env.now+self.env_start}): Bus {self.name} loaded {num_people_to_board} people from {self.get_current_stop()} ({load_time} mins)"
        )

    def deload_passengers(self) -> None:
        # Currently all passengers get off...
        get_off = self.passenger_count()

        if not get_off:
            print(
                f"({self.env.now+self.env_start}): No passengers got off the bus {self.name}"
            )
            return

        off_time = int(get_off * PERSON_BOARD_TIME)
        yield self.env.timeout(off_time)
        print(
            f"({self.env.now+self.env_start}): Bus {self.name} has dropped off {get_off} people at {self.get_current_stop()} ({off_time} mins)"
        )
        self.route.stops[self.location_index].put(self.passengers)
        self.passengers.clear()

    def passenger_count(self) -> int:
        return sum(group.get_num_people() for group in self.passengers)


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

            have_distributed += num_for_stop
            print(
                f"({self.env.now+self.env_start}): {num_for_stop} people arrived at {stop.name} in {self.name}"
            )

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

    bus_route = Route(
        env=env,
        name="the_route",
        transport_type="Bus",
        stops=[first_stop, last_stop],
        env_start=env_start,
    )
    walk_to_stadium = Route(
        env=env,
        name="the_walk",
        transport_type="Walking",
        stops=[last_stop, stadium],
        env_start=env_start,
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
    simple_example(env, START_TIME, get_data(env, env_start=START_TIME))
