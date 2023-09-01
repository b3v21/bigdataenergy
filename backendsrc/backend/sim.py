from __future__ import annotations
import itertools
import random
from simpy import Environment, Resource
import math
import numpy as np
from pathlib import Path
import os
import sys
import django

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
        return f'Count: {self.get_num_people()}, Start Time: {self.get_start_time()}, End Time: {self.get_end_time()}, Journey Time: {self.get_end_time() - self.get_start_time() if self.get_end_time() != None else "N/A"}, Start Loc: {self.start_location.name}'

    def get_num_people(self) -> int:
        return self.num_people

    def add_start_loc(
        self, location: Station
    ) -> None:  # Changed Location to busStop, for now
        self.start_location = location

    def get_num_people(self) -> int:
        return self.num_people

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
    down the line we can gather a walking congestion coefficient if multiple instances of walking
    that are within a certain proximity and pass some quantity threshold occur...
    """

    WALKING_CONGESTION = 1  # Temp

    def __init__(
        self,
        env: Environment,
        start_pos: tuple[int, int] | Station,  # Think about this later
        end_pos: tuple[int, int] | Station,
        people: list[People],
    ) -> None:
        self.env = env
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.people = people

    def walk(self) -> None:
        """
        Walking process
        """
        walk_time = self.walk_time() * Walking.WALKING_CONGESTION
        print(
            f"({self.env.now}): {self.get_num_people()} have started walking from {self.start_pos.name} to {self.end_pos.name} (Expect to take {walk_time})"
        )
        yield self.env.timeout(walk_time)
        print(
            f"({self.env.now}): {self.get_num_people()} have finished walking from {self.start_pos.name} to {self.end_pos.name}"
        )
        self.end_pos.put(self.people)

    def get_num_people(self) -> int:
        return sum(group.get_num_people() for group in self.people)

    def walk_time(self) -> int:
        """
        Reponsible for calculating the walk time between two locations (use google maps api)
        """
        return random.randint(5, 20)


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
        people: list[People],
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
        self.people = people
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

    def put(self, passengers: list[People], suburb=False) -> None:
        for people in passengers:
            if not suburb and not people.itinerary.last_leg():
                people.itinerary.next()
            if people.itinerary.last_leg():
                # Being put at end
                self.people.append(people)
            elif people.itinerary.get_current_type() == "Bus":
                self.people.append(people)
            elif people.itinerary.get_current_type() == "Walking":
                # Queue people all up to walk
                self.env.process(
                    Walking(
                        self.env,
                        self,
                        people.itinerary.get_current_route().last_stop,
                        [people],
                    ).walk()
                )  # Currently doing each individual cluster on own walk chunk --> can change?

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
                    f"({self.env.now+self.env_start}): Bus {name} is starting on route {self.name}"
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
            print(
                f"({self.env.now+self.env_start}): Bus {self.name} is arriving stop {self.get_current_stop()}"
            )
            with self.route.stops[self.location_index].bays.request() as req:
                yield req
                if self.route.stops[(self.location_index)] != self.route.last_stop:
                    yield self.env.process(self.load_passengers())
                else:
                    yield self.env.process(self.deload_passengers())

                next = (self.location_index + 1) % len(self.route.stops)

            print(
                f"({self.env.now+self.env_start}): Bus {self.name} is leaving from stop {self.get_current_stop()} to go to {self.route.stops[next].name}"
            )

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

            self.location_index = next
            self.update_current_stop()
            yield self.env.timeout(travel_time)

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
            # add functionality in here
            return

        people_to_ride = self.route.stops[self.location_index].board(
            min(people_at_stop, bus_seats_left)
        )

        num_people_to_board = sum([p.get_num_people() for p in people_to_ride])
        load_time = num_people_to_board * PERSON_BOARD_TIME
        self.passengers += people_to_ride

        yield self.env.timeout(load_time)

        print(
            f"({self.env.now+self.env_start}): Bus {self.name} has loaded {num_people_to_board} people from {self.get_current_stop()}"
        )

    def deload_passengers(self) -> None:
        # Currently all passengers get off...
        get_off = self.passenger_count()

        if not get_off:
            print(
                f"({self.env.now+self.env_start}): No passengers got off the bus {self.name}"
            )
            return

        off_time = get_off * PERSON_BOARD_TIME
        yield self.env.timeout(off_time)
        print(
            f"({self.env.now+self.env_start}): Bus {self.name} has dropped off {get_off} people at {self.get_current_stop()}"
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
        stations: dict[Station, float],
        population: int,
        frequency: int,
        max_distributes: int,
        iteneraries: list[Itinerary],
        env_start: int,
    ) -> None:
        self.env = env
        self.env_start = env_start
        self.name = name
        self.stations = stations
        self.population = population
        self.frequency = frequency  # How often to try and distribute the population
        self.max_distributes = max_distributes
        self.itenteraries = iteneraries

        # Start process
        self.pop_proc = self.env.process(self.suburb())

    def suburb(self) -> None:
        """
        Process for the existence of the suburb object.
        Every frequency minutes, will distribute random* amount of population to nearby suburbs.
        """
        distributes = 0

        while distributes <= self.max_distributes:
            if self.env.now % self.frequency == 0:
                # Distribute population
                to_dist = (
                    random.randint(0, self.population)
                    if distributes < self.max_distributes
                    else self.population
                )
                have_distributed = 0

                # Will need to change when handling different stop types
                for stop in self.stations.keys():
                    num_for_stop = math.floor(
                        self.stations[stop] / 100 * (to_dist - have_distributed)
                    )
                    if num_for_stop == 0:
                        continue
                    if stop == list(self.stations.keys())[-1]:
                        num_for_stop = (
                            to_dist - have_distributed
                        )  # To account for rounding
                    stop.put(
                        [
                            People(
                                self.env,
                                num_for_stop,
                                self.env.now,
                                stop,
                                self.itenteraries[
                                    random.randint(0, len(self.itenteraries) - 1)
                                ].duplicate(suburb=True),
                                self.env_start,
                            )
                        ]
                    )
                    have_distributed += num_for_stop
                    if num_for_stop != 0:
                        print(
                            f"({self.env.now+self.env_start}): {num_for_stop} new people have just arrived at {stop.name} in {self.name}"
                        )
            distributes += 1
            self.population -= have_distributed
            yield self.env.timeout(1)


def distance_between(stop1: Station, stop2: Station) -> int:
    """
    This may be based off of calculation or database of data, effectively, return the
    time it takes to travel between two locations
    """

    dist = math.sqrt(
        math.pow((stop1.pos[0] - stop2.pos[0]), 2)
        + math.pow((stop1.pos[1] - stop2.pos[1]), 2)
    )
    BUSY_LEVEL = 1  # TEMP ----------------------------------------------------
    time = math.floor(dist * BUSY_LEVEL)

    return time


def complex_example() -> None:
    env = Environment()

    group1 = People(env, random.randint(0, 50), 0)
    group2 = People(env, random.randint(0, 50), 4)
    group3 = People(env, random.randint(0, 50), 8)
    group4 = People(env, random.randint(0, 50), 16)

    cultural_centre_bus_station = Station(
        env, "Cultural Centre Station", (0, 0), 1, [group1], 10, 2
    )
    king_george_square_bus_station = Station(
        env, "King George Square Bus Station", (0, 3), 2, [group2]
    )
    roma_street_busway_station = Station(
        env, "Roma Street Busway Station", (0, 5), 3, [group3]
    )
    given_tce_bus_stop = Station(env, "Given Tce Bus Stop", (0, 7), 1, [group4])

    Route(
        env,
        "385",
        [
            cultural_centre_bus_station,
            king_george_square_bus_station,
            roma_street_busway_station,
            given_tce_bus_stop,
        ],
    )
    Route(
        env,
        "385B",
        [
            cultural_centre_bus_station,
            king_george_square_bus_station,
            roma_street_busway_station,
            given_tce_bus_stop,
        ],
    )
    env.run(30)


def simple_example(
    env: Environment, env_start: int, data: tuple(list[Station], list[Route])
) -> None:
    stations, routes = data
    ROUTE_ID = 66

    itinerary = Itinerary(env, 0, [routes[ROUTE_ID]])

    Suburb(
        env,
        "Simple Suburb",
        {
            routes[ROUTE_ID].get_stations()[0]: 100,
            routes[ROUTE_ID].get_stations()[-1]: 0,
        },
        100,
        10,
        0,
        [itinerary],
        env_start,
    )

    env.run(120)


# def simple_example() -> None:
#     env = Environment()

#     first_stop = Station(env, "first_stop", "Bus", (0, 0), 1, [], 1, 1)
#     last_stop = Station(env, "last_stop", "Bus", (2, 2), 1, [], 3)
#     stadium = Station(env, "stadium", "Finish", (4, 4), 1, [])

#     bus = Route(env, "the_route", "Bus", [first_stop, last_stop])
#     walking = Route(env, "the walk", "Walking", [last_stop, stadium])
#     itinerary = Itinerary(env, 0, [bus, walking])

#     simple_suburb = Suburb(
#         env, "Simple Suburb", {first_stop: 100, last_stop: 0}, 100, 10, 0, [itinerary]
#     )
#     env.run(30)
#     print(first_stop)
#     print(last_stop)
#     print(stadium)


def get_data(env, env_start=0):
    stations = StationM.objects.all()
    routes = RouteM.objects.all()
    timetables = TimetableM.objects.all()

    station_objects = {}
    route_objects = {}

    for station in stations:
        qs = timetables.filter(station_id=station.station_id)
        st_timetables = {}
        for st_timetable in qs:
            times_stripped = st_timetable.arrival_times.strip("[").strip("]").split(",")
            formated_times = [round(float(time.strip(' \'').split(":")[0]) + (float(time.strip(' \'').split(":")[1]) / 60),2) for time in times_stripped]
            st_timetables[st_timetable.route_id] = formated_times
        
        station_objects[station.station_id] = Station(
            env,
            station.station_id,
            station.name,
            (station.lat, station.long),
            1,  # bays currently always 1
            [],  # No initial people
            env_start=env_start,
            bus_timings= st_timetables,  # BUS TIMINGS FOR THIS STATION, FROM TIMETABLE TABLE
            bus_spawn_max=0,
        )

    for route in routes:
        route_stations = timetables.filter(route_id=route.route_id).values_list("station_id")
        route_stations_list = [station_objects[station[0]] for station in route_stations]
        
        route_objects[route.route_id] = Route(
            env,
            route.name,
            "Bus", # Hard codied for now
            route_stations_list, # GET STATIONS FOR A GIVEN ROUTE
            env_start
        )

    return (station_objects, route_objects)

if __name__ == "__main__":
    env = Environment()
    simple_example(env, START_TIME, get_data(env, env_start=START_TIME))
