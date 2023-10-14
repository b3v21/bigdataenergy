from __future__ import annotations
from simpy import Environment, Resource
from abc import ABC, abstractmethod
from random import randint, randrange, choice
from pathlib import Path
from math import ceil, floor
import django
import os
import sys
from datetime import time, date, datetime
import time as t
import requests
import json
import numpy as np


sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from db.models import (
    Station as StationM,
    Route as RouteM,
    Timetable as TimetableM,
    Trip as TripM,
    Shape as ShapeM,
    Calendar as CalendarM,
    StationSim,
    RouteSim,
    ItinerarySim,
    SimulationOutput,
    BusOnRouteInfo,
    PassengerChanges,
    BusTimeOut,
)  # noqa: E402


PERSON_BOARD_TIME = 0.1
MINUTES_IN_DAY = 1440
MINUTES_IN_HOUR = 60
DEBUG = True

# THIS IS FOR STORING ITINERARY OBJECTS PRODUCED BY THE SIM
ITINERARIES = []


def convert_date_to_int(time: time) -> int:
    return time.hour * MINUTES_IN_HOUR + time.minute


class Itinerary:
    """
    Object to store multiple types of travel at a time.
    """

    def __init__(
        self, env: Environment, id: int, routes: list[tuple[Route, Station | None]]
    ):
        self.env = env
        self.routes = routes
        self.id = id

    def __str__(self):
        return f"Itinerary: ID: {self.id}, Routes: {self.routes}"

    def get_current_type(self, people: People) -> str:
        return self.routes[people.current_route_in_itin_index][0].get_type()

    def get_current(self, people: People) -> Route:
        return self.routes[people.current_route_in_itin_index]

    def get_current_route(self, people: People) -> Route:
        return self.routes[people.current_route_in_itin_index][0]

    def last_leg(self, people: People) -> bool:
        return people.current_route_in_itin_index == len(self.routes) - 1


class People:
    """
    A group of people which will travel along a route.
    """

    num_in_simulation = 0
    all_people = []

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
        self.current_route_in_itin_index = current_route_in_itin_index
        self.people_log = {}
        People.all_people.append(self)
    
    

    def log(self, where: tuple[str, int]) -> None:
        self.people_log[self.env.now + self.env_start] = where

    def __str__(self) -> str:
        journey_time = (
            self.end_time - self.start_time if self.end_time != None else "N/A"
        )

        return f"Count: {self.get_num_people()}, Start Time: {self.start_time}, End Time: {self.end_time}, Journey Time: {journey_time}, Start Loc: {self.start_location.name}"

    def get_num_people(self) -> int:
        return self.num_people

    def change_num_people(self, change: int) -> None:
        self.num_people += change

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
        id: str,
        name: str,
        pos: tuple[float, float],
        bays: int,
        env_start: int,
        itin: int = None,  # By default has no itin, only active ones have index of itin
    ) -> None:
        self.env_start = env_start
        self.env = env
        self.id = id
        self.name = name
        self.pos = pos
        self.bays = Resource(env, capacity=bays)
        self.people = []
        self.people_over_time = {}
        self.station = None  # None on init, will be assigned by Suburb init
        self.itin = itin
        self.log_cur_people()

    def log_cur_people(self) -> None:
        self.people_over_time[self.env.now + self.env_start] = self.num_people()

    def __str__(self) -> str:
        output = f"{self.name}: Total People = {self.num_people()}, Total Groups = {len(self.people)}"
        for people in self.people:
            output += f"\n{str(people)}"
        return output

    def board(self, num_people_to_board: int, route: Route) -> list[People]:
        """
        Given the number of people who are at the stop, this method returns a list
        'people_to_get' containing the people which a bus can collect from this stop.
        """

        cur_total = 0
        people_to_get = []

        for people in self.people:
            if ITINERARIES[people.itinerary_index].get_current_route(people) != route:
                continue  # They dont want to board this
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
                split.people_log = {k: v for (k, v) in people.people_log.items()}
                people.change_num_people(-excess)
                self.people.append(split)
                people_to_get.append(people)
                break
            people_to_get.append(people)
            cur_total += people.get_num_people()
            if cur_total == num_people_to_board:
                break

        for p in people_to_get:
            self.people.remove(p)
        return people_to_get

    def put(self, passengers: list[People], from_suburb=False) -> None:
        for group in passengers:
            group.log((self.name, self.id))

            if not ITINERARIES[group.itinerary_index].last_leg(group) and (
                ITINERARIES[group.itinerary_index].get_current(group)[1] == self
                or ITINERARIES[group.itinerary_index].get_current_route(group).last_stop
                == self
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
                self.people.append(group)
                self.env.process(
                    ITINERARIES[group.itinerary_index]
                    .get_current_route(group)
                    .walk_instance(group, time_to_wait)
                )

        self.log_cur_people()

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
        route: Route,
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
        self.route = route

    def get_name(self) -> str:
        return f"{self.name}"

    def load_passengers(self, station: Station) -> None:
        """Load passengers from the current stop onto this transporter."""

        seats_left = self.capacity - self.passenger_count()
        people_at_stop = sum(group.get_num_people() for group in station.people)
        if not people_at_stop:
            if DEBUG:
                print(
                    f"({self.env.now+self.env_start}): No passengers at stop {station.name}"
                )
            return

        if not seats_left:
            if DEBUG:
                print(
                    f"({self.env.now+self.env_start}): No seats left on bus {self.get_name()}"
                )
            return

        people_to_ride = station.board(min(people_at_stop, seats_left), self.route)
        num_people_to_board = sum([p.get_num_people() for p in people_to_ride])
        load_time = int(num_people_to_board * PERSON_BOARD_TIME)
        self.people += people_to_ride

        yield self.env.timeout(load_time)
        station.log_cur_people()
        for people in people_to_ride:
            people.log((self.name, self.id))
        if DEBUG:
            print(
                f"({self.env.now+self.env_start}): {self.get_type()} {self.get_name()} loaded {num_people_to_board} people from {station.name} ({load_time} mins)"
            )

    def get_people_deloading(self, station: Station) -> list[People]:
        people = []
        for group in self.people:
            gets_off_at = ITINERARIES[group.itinerary_index].get_current(group)[1]
            if gets_off_at == station:
                people.append(group)
        return people

    def deload_passengers(self, station: Station) -> None:
        people_deloading = []
        if self.route.last_stop == station:
            # Everyone left needs to get off
            people_deloading = self.people
        else:
            # Only those who want to get off should get off
            people_deloading = self.get_people_deloading(station)

        num_passengers_deloaded = sum(p.get_num_people() for p in people_deloading)

        if not num_passengers_deloaded:
            if DEBUG:
                print(
                    f"({self.env.now+self.env_start}): No passengers got off {self.get_type()}: {self.get_name()}"
                )
            return

        deload_time = int(num_passengers_deloaded * PERSON_BOARD_TIME)
        yield self.env.timeout(deload_time)
        if DEBUG:
            print(
                f"({self.env.now+self.env_start}): {self.get_type()} {self.get_name()} has dropped off {num_passengers_deloaded} people at {station.name} ({deload_time} mins)"
            )

        station.put(people_deloading)

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
        route: Route,
        location_index: int = 0,
        people: list[People] = [],
        capacity: int = 50,
    ) -> None:
        super().__init__(
            env, env_start, id, name, trip, route, location_index, people, capacity
        )
        self.bus_time_log = {}
        self.bus_passenger_changes = {}

    def get_type(self) -> str:
        return "Bus"

    def __str__(self) -> str:
        return f"{self.id}, {self.trip}, {self.location_index}, {self.people}, {self.capacity}"

    def bus_instance(self, bus_route: BusRoute) -> None:
        self.bus_passenger_changes[
            self.env.now + self.env_start
        ] = self.passenger_count()
        while True:
            with bus_route.get_current_stop(self).bays.request() as req:
                yield req
                if DEBUG:
                    print(
                        f"({self.env.now+bus_route.env_start}): Bus {self.get_name()} arrived at {bus_route.get_current_stop(self).name}"
                    )
                self.bus_time_log[
                    f"{bus_route.get_current_stop(self).name} ({bus_route.get_current_stop(self).id})"
                ] = (self.env.now + self.env_start)
                if bus_route.get_current_stop(self) != bus_route.last_stop:
                    prev_passenger_count = self.passenger_count()

                    yield self.env.process(
                        self.load_passengers(bus_route.get_current_stop(self))
                    )

                    yield self.env.process(
                        self.deload_passengers(bus_route.get_current_stop(self))
                    )

                    if prev_passenger_count != self.passenger_count():
                        self.bus_passenger_changes[
                            self.env.now + self.env_start
                        ] = self.passenger_count()

                else:
                    yield self.env.process(
                        self.deload_passengers(bus_route.get_current_stop(self))
                    )
                    self.bus_passenger_changes[
                        self.env.now + self.env_start
                    ] = self.passenger_count()
                    # Despawn
                    if DEBUG:
                        print(
                            f"({self.env.now+bus_route.env_start}): Bus {self.get_name()} ended its journey."
                        )
                    break

                previous_stop = bus_route.stops[self.location_index]
                self.move_to_next_stop(len(bus_route.stops))
                cur_stop = bus_route.get_current_stop(self)
                travel_time = 0
                index = 0
                for stop, time in self.trip.timetable:
                    if cur_stop.name == stop:
                        travel_time = time - self.trip.timetable[index - 1][1]
                        break
                    index += 1
                if travel_time == 0:
                    # Some bus stops have very small distances between, to stop teleportation, make min one
                    print("**Had a case where travel time was 0**")
                    travel_time = 1

                if travel_time < 0:
                    if DEBUG:
                        print("***ERROR*** Travel time <= 0!!!")
                        exit()
                    travel_time = 1

            yield self.env.timeout(travel_time)
            if DEBUG:
                print(
                    f"({self.env.now+bus_route.env_start}): Bus {self.get_name()} travelled from {previous_stop.name} to {bus_route.get_current_stop(self).name} ({travel_time} mins)"
                )


class Train(Transporter):
    """A train moving through a route"""

    def __init__(
        self,
        env: Environment,
        env_start: int,
        id: int,
        name: str,
        trip: Trip,
        route: Route,
        location_index: int = 0,
        people: list[People] = [],
        capacity: int = 50,
    ) -> None:
        super().__init__(
            env, env_start, id, name, trip, route, location_index, people, capacity
        )

    def get_type(self) -> str:
        return "Train"

    def __str__(self) -> str:
        return f"{self.id}, {self.trip}, {self.location_index}, {self.people}, {self.capacity}"

    def train_instance(self, train_route: TrainRoute) -> None:
        while True:
            with train_route.get_current_stop(self).bays.request() as req:
                yield req
                if DEBUG:
                    print(
                        f"({self.env.now+train_route.env_start}): Train {self.get_name()} arrived at {train_route.get_current_stop(self).name}"
                    )
                if train_route.get_current_stop(self) != train_route.last_stop:
                    yield self.env.process(
                        self.load_passengers(train_route.get_current_stop(self))
                    )

                    yield self.env.process(
                        self.deload_passengers(train_route.get_current_stop(self))
                    )
                    self.bus_passenger_changes[
                        self.env.now + self.env_start
                    ] = self.passenger_count()

                else:
                    yield self.env.process(
                        self.deload_passengers(train_route.get_current_stop(self))
                    )
                    self.bus_passenger_changes[
                        self.env.now + self.env_start
                    ] = self.passenger_count()
                    # Despawn
                    if DEBUG:
                        print(
                            f"({self.env.now+train_route.env_start}): Bus {self.get_name()} ended its journey."
                        )
                    break

                previous_stop = train_route.stops[self.location_index]
                self.move_to_next_stop(len(train_route.stops))
                cur_stop = train_route.get_current_stop(self)
                travel_time = 0
                index = 0
                for stop, time in self.trip.timetable:
                    if cur_stop.name == stop:
                        travel_time = time - self.trip.timetable[index - 1][1]
                        break
                    index += 1
                if travel_time == 0:
                    # Some bus stops have very small distances between, to stop teleportation, make min one
                    print("**Had a case where travel time was 0**")
                    travel_time = 1

                if travel_time < 0:
                    if DEBUG:
                        print("***ERROR*** Travel time <= 0!!!")
                        exit()
                    travel_time = 1

            yield self.env.timeout(travel_time)
            self.bus_time_log[train_route.get_current_stop(self).name] = (
                self.env.now + self.env_start
            )
            if DEBUG:
                print(
                    f"({self.env.now+train_route.env_start}): Bus {self.get_name()} travelled from {previous_stop.name} to {train_route.get_current_stop(self).name} ({travel_time} mins)"
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

    def initiate_route(self) -> None:
        """
        A function to initiate the route. Will spawn busses on the according time
        intervals and then handle how these buses transport people along the route
        """

        trips_to_iniate = self.trip_timing_data
        while True:
            station_info = None
            trip_info = None
            trips_inited = []
            for trip in trips_to_iniate:
                for station, arrival_time in trip.timetable:
                    if (
                        arrival_time == (self.env.now + self.env_start)
                        and self.transporter_spawn_max != self.transporters_spawned
                    ):
                        station_info = (station, arrival_time)
                        trip_info = trip
                        # Now have a trip to start
                        new_bus = Bus(
                            env=self.env,
                            env_start=self.env_start,
                            id=self.transporters_spawned,
                            name=f"B{self.transporters_spawned}_{self.name}",
                            trip=trip_info,
                            route=self,
                            location_index=self.get_stop_with_name(station_info[0]),
                            people=[],
                        )
                        self.transporters_spawned += 1
                        self.add_bus(new_bus)
                        # if trip.timetable[0][0] == station:
                        #     print(
                        #         f"({self.env.now+self.env_start}): Bus {new_bus.get_name()} started on route {self.name} at station {station_info[0]}"
                        #     )
                        # else:
                        #     print(
                        #         f"({self.env.now+self.env_start}): Bus {new_bus.get_name()} already on route {self.name} at station {station_info[0]}"
                        #     )
                        self.env.process(new_bus.bus_instance(self))
                        trips_inited.append(trip)
            for trip in trips_inited:
                trips_to_iniate.remove(trip)

            yield self.env.timeout(1)

    def get_type(self) -> str:
        return "BusRoute"

    def add_bus(self, new_bus: Bus) -> None:
        self.buses.append(new_bus)

    def get_current_stop(self, bus: Bus) -> Station:
        return self.stops[bus.location_index]

    def get_stop_with_name(self, name: str) -> Station:
        return [stop.name for stop in self.stops].index(name)


class TrainRoute(Route):
    """
    A route for trains to take. This works similarly to the BusRoute class, but more care needs to
    be taken when spawning trains on routes as it needs to be ensured that collisions do not
    occur.
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
        self.trains: list[Train] = []

    def initiate_route(self) -> None:
        """
        A function to initiate the route. Will spawn trains at stops according to the trip timing
        data. TODO: will the trip timing data be all that is required to correctly spawn
        trains? Or will we also need additional information to ensure that trains do not
        collide?
        """
        trips_to_iniate = self.trip_timing_data
        while True:
            station_info = None
            trip_info = None
            trips_inited = []
            for trip in trips_to_iniate:
                for station, arrival_time in trip.timetable:
                    if arrival_time == (self.env.now + self.env_start):
                        station_info = (station, arrival_time)
                        trip_info = trip
                        # Now have a trip to start
                        new_train = Train(
                            env=self.env,
                            env_start=self.env_start,
                            id=self.transporters_spawned,
                            name=f"B{self.transporters_spawned}_{self.name}",
                            trip=trip_info,
                            route=self,
                            location_index=self.get_stop_with_name(station_info[0]),
                            people=[],
                        )
                        self.transporters_spawned += 1
                        self.add_train(new_train)
                        # if trip.timetable[0][0] == station:
                        #     print(
                        #         f"({self.env.now+self.env_start}): Train {new_train.get_name()} started on route {self.name} at station {station_info[0]}"
                        #     )
                        # else:
                        #     print(
                        #         f"({self.env.now+self.env_start}): Train {new_train.get_name()} already on route {self.name} at station {station_info[0]}"
                        #     )
                        self.env.process(new_train.train_instance(self))
                        trips_inited.append(trip)
            for trip in trips_inited:
                trips_to_iniate.remove(trip)

            yield self.env.timeout(1)

    def get_type(self) -> str:
        return "TrainRoute"

    def add_train(self, new_train: Train) -> None:
        self.trains.append(new_train)

    def get_current_stop(self, train: Train) -> Station:
        return self.stops[train.location_index]

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
        self.first_stop.people.remove(people)
        people.log((None, self.id))
        self.walk_time_log[people] = [self.env.now + self.env_start, None]
        self.people.append(people)
        self.stops[0].log_cur_people()
        walk_time = self.walk_time() * self.walking_congestion
        yield self.env.timeout(walk_time)
        self.people.remove(people)
        self.walk_time_log[people][1] = self.env.now + self.env_start
        self.stops[1].put([people])
        if DEBUG:
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
        stations: list[Station],
        population: int,
        frequency: int,
        max_distributes: int,
        active: bool,
        env_start: int,
    ) -> None:
        self.env = env
        self.env_start = env_start
        self.name = name
        self.station_distribution = station_distribution
        for station in self.station_distribution.keys():
            station.suburb = self  # Depending on use case for this, may change to id
        self.population = population
        self.frequency = frequency  # How often to try and distribute the population
        self.max_distributes = max_distributes
        self.active = active

        # Start process IF active
        if active:
            self.pop_proc = self.env.process(self.suburb())

    def suburb(self) -> None:
        """
        Every frequency minutes, will distribute random amount of population to nearby
        stations.
        """
        current_distribution = 0

        while current_distribution < self.max_distributes:
            if (self.env.now + self.env_start) % self.frequency == 0:
                have_distributed = self.distribute_people(
                    ceil(self.population / (self.max_distributes))
                )

                current_distribution += 1
                self.population -= have_distributed
            yield self.env.timeout(1)

        # distribute remaining people if there are any
        if self.population > 0:
            _ = self.distribute_people(self.population)

    def distribute_people(self, num_people: int) -> int:
        """
        Current assigns random amount of people to each of the active stations within this active suburb.
        """
        people_distributed = 0
        while people_distributed != num_people:
            possible_stations = list(self.station_distribution.keys())

            if not possible_stations:
                continue
            station = choice(possible_stations)
            if not self.station_distribution[station]:
                continue

            num_for_stop = ceil((self.station_distribution[station] / 100) * num_people)

            if num_for_stop > num_people - people_distributed:
                num_for_stop = num_people - people_distributed

            people_arriving_at_stop = People(
                env=self.env,
                count=num_for_stop,
                start_time=self.env.now,
                start_location=station,
                itinerary_index=station.itin,
                current_route_in_itin_index=0,  # SHOULD always be 0, each active station has unique itin.
                env_start=self.env_start,
            )

            station.put([people_arriving_at_stop], from_suburb=True)
            People.num_in_simulation += people_arriving_at_stop.get_num_people()

            if DEBUG:
                print(
                    f"({self.env.now+self.env_start}): {num_for_stop} people arrived at {station.name} in {self.name}"
                )

            people_distributed += num_for_stop
        return people_distributed


class Trip:
    """This trip object will be created to hold transporter timings"""

    def __init__(self, timetable: list[tuple[str, int]]) -> None:
        self.timetable = timetable


def run_simulation(
    user_data: dict[dict], sim_id: int
) -> tuple[list[Station], list[Trip], list[Route], list[Itinerary], int, dict[dict]]:
    """Main function to run the simulation"""

    env = Environment()

    stations, trips, routes, itineraries, suburbs = get_data(
        env,
        user_data["env_start"],
        user_data["time_horizon"],
        user_data["itineraries"],
        user_data["snapshot_date"],
        user_data["active_suburbs"],
        user_data["active_stations"],
    )

    print(f"Models successfully created for simulation #{sim_id}.")
    env.run(user_data["time_horizon"])
    print(f"Simulation #{sim_id} successfully ran.")
    output = process_simulation_output(stations, routes, itineraries, sim_id, trips)
    print(f"Simulation #{sim_id} output processed.")
    load_sim_data_into_db(stations, routes, itineraries, sim_id)

    return output


def process_simulation_output(
    stations: list[Station],
    routes: list[Route],
    itineraries: list[Itinerary],
    sim_id: int,
    trips: list[Trip],
) -> dict[dict]:
    """
    Analyse all the models once the simulation has finished running and returns the
    information which will be sent to the frontend.

    output has the following format:

    output = {
        "SimulationID": sim_id,
        "Routes": [
            route_id: {
                "method": "BusRoute" or "Walk",
                "TransportersOnRoute": {
                    transporter_id: {
                        "Timeout": {...},
                        "PassengerChangesOverTime": {...},
                    },
                },
                "shape" : [("sequence", "lat", "long"), ...)]
                "Walkout": {walk_id: time, ...},
                "stations": {
                    station_id: {
                        "stationName": station_name,
                        "pos": {
                            "lat": lat,
                            "long": long
                        }
                        "seq": int
                    }
                }
            },
        ],
        "Stations": [
            station_id: {
                "stationName": station_name,
                "pos": {
                    "lat": lat,
                    "long": long
                },
                "avg_wait" : avg_wait,
                "PeopleChangesOverTime": {time: num_people, ...},
                "bottleneck" : True/False
            },
        ],
        "Itineraries": [
            itinerary_id: {
                "Routes": {
                    route_id: {station_name, ...}
                }
            }
        ],
        "Bottlenecks": [
            station_ids
        ]
    }
    """

    output = {"Simulation_id": sim_id, "Routes": {}, "Stations": {}, "Itineraries": {}}

    for route in routes:
        output["Routes"][route.id] = {}
        rd = output["Routes"][route.id]
        rd["method"] = route.get_type()
        if route.get_type() == "BusRoute":
            rd["BusesOnRoute"] = {}
            br = rd["BusesOnRoute"]
            shape_id = TripM.objects.filter(route_id=route.id).first().shape_id.shape_id  
            shapes = ShapeM.objects.filter(shape_id=shape_id)
            
            shape_out = [(shape.shape_pt_sequence, shape.shape_pt_lat, shape.shape_pt_lon) for shape in shapes]
            shape_out.sort(key=lambda x: x[0])
            shape_out = [{"sequence" : i, "lat" : b, "long" : c} for i, (a,b,c) in enumerate(shape_out)]
            
            rd["shape"] = shape_out
            for bus in route.buses:
                br[bus.id] = {
                    "Timeout": bus.bus_time_log,
                    "PassengerChangesOverTime": bus.bus_passenger_changes,
                }
        elif route.get_type() == "Walk":
            rd["Walkout"] = route.walk_time_log

        rd["stations"] = {}
        for station in route.stops:
            rd["stations"][station.id] = {}
            sd = rd["stations"][station.id]
            sd["stationName"] = station.name
            sd["pos"] = {
                "lat": station.pos[0],
                "long": station.pos[1],
            }
            sd["sequence"] = route.stops.index(station)

    """
    This process isnt entirely perfect, the error will cut out some of the indexing issues.
    However this dict will still extract info it thinks is about a station even tho its not.
    This will be fixed by accessing only valid entries from within station parsing.
    """
    people = People.all_people
    station_waits = {}
    station_groups = {}
    for group in people:
        log = group.people_log
        index = 0
        for time, entry in log.items():
            try:
                if index != len(list(log.keys())) - 1:
                    if entry[1] not in station_waits:
                        station_waits[entry[1]] = [list(log.keys())[index + 1] - time]
                    else:
                        station_waits[entry[1]].append(list(log.keys())[index + 1] - time)
                else:
                    #Is the last entry in log
                    end_sim = station.env_start + station.env.now
                    if entry[1] not in station_waits:
                        station_waits[entry[1]] = [end_sim - time]
                    else:
                        station_waits[entry[1]].append(end_sim - time)
                if entry[1] not in station_groups:
                    station_groups[entry[1]] = 1
                else:
                    station_groups[entry[1]] += 1
            except:
                #Format error
                pass
            index += 1


    destination = itineraries[0].routes[-1][1]

    num_arrived = destination.num_people()
    num_late = People.num_in_simulation - num_arrived

    
    """
    Calculating outliers only looks at stations who HAVE an average waiting time.
    Stations without one have N/A and would polute data set with impossible to beat times.
    """
    avg_wait_times = {}
    bottles = {}
    for station in stations:
        output["Stations"][station.id] = {}
        sd = output["Stations"][station.id]
        sd["stationName"] = station.name
        sd["pos"] = {
            "lat": station.pos[0],
            "long": station.pos[1],
        }
        if station.id in station_waits:
            sd["avg_wait"] = sum(station_waits[station.id])/len(station_waits[station.id])
            avg_wait_times[station.id] = sum(station_waits[station.id])/len(station_waits[station.id])
        else:
            sd["avg_wait"] = "N/A"
        sd["PeopleChangesOverTime"] = station.people_over_time
    data = np.array(list(avg_wait_times.values()))

    mean = np.mean(data)
    std = np.std(data)
    
    threshold = 1 # May need tweaking ---
    outliers = []
    for x in data:
        z = (x - mean) / std
        if abs(z) > threshold and x > mean:
            outliers.append(x)

    for station in stations:
        sd = output["Stations"][station.id]
        if sd["avg_wait"] in outliers:
            sd["bottleneck"] = True
            bottles[station.id] = True
        else:
            sd["bottleneck"] = False


    percentage_arrived = (num_arrived)/(num_late + num_arrived) * 100


    for itinerary in itineraries:
        output["Itineraries"][itinerary.id] = {}
        itin_d = output["Itineraries"][itinerary.id]
        itin_d["Routes"] = {}
        for route_tuple in itinerary.routes:
            route = route_tuple[0]
            itin_d["Routes"][route.id] = set()
            rd = itin_d["Routes"][route.id]
            for stop in route.stops:
                rd.add(stop.name)
    output["Bottlenecks"] = list(bottles.values())
    return output


def get_data(
    env: Environment,
    env_start: int,
    time_horizon: int,
    itineraries: list,  # Go to views.py for format
    snapshot_date: str,
    active_suburbs: list[str],
    active_stations: list[str],
) -> tuple[
    dict[int, Station], list[Trip], dict[int, BusRoute], list[Itinerary], list[Suburb]
]:
    """
    This function accesses the data from the database and converts it into simulation
    objects.
    """

    if not snapshot_date:
        snapshot_date = datetime.date.today()
    else:
        snapshot_date = datetime.strptime(snapshot_date, "%Y-%m-%d").date()

    day_of_week = snapshot_date.strftime("%A").lower()

    # Get all calendar objects (containing service info) that run on the requested d.o.t.w
    calendars = CalendarM.objects.all().filter(
        start_date__lte=snapshot_date, end_date__gte=snapshot_date, **{day_of_week: 1}
    )

    # Get all routes that are used in the itineraries
    route_ids = {}
    walks = {}
    walk_id = 0

    for itinerary in itineraries:
        for route in itinerary["routes"]:
            route_id = route["route_id"]
            start = route["start"]
            end = route["end"]

            if route_id != "walk":
                route_ids[route_id] = end
            else:
                # Walk
                walks[f"Walk_{walk_id}"] = (start, end)
                walk_id += 1

    db_routes = RouteM.objects.all().filter(route_id__in=list(route_ids.keys()))

    sim_routes = {}
    sim_trips = []
    sim_stations = {}

    for route in db_routes:
        # Get trip_ids that run on this day for this particular route
        db_trips = TripM.objects.all().filter(service_id__in=calendars, route_id=route)
        if not db_trips:
            raise Exception(
                f"No trips exist for route {route.name} on {snapshot_date.strftime('%Y-%m-%d')}"
            )

        if not db_trips:
            continue

        route_stations = {}
        route_trips = []

        ## Create sim Trips ##
        for trip in db_trips:
            # Get Timetables for that trip
            sim_timetables = []
            db_timetables = (
                TimetableM.objects.all().filter(trip_id=trip).order_by("sequence")
            )

            for timetable in db_timetables:
                sim_timetables.append(
                    (
                        timetable.station.name,
                        convert_date_to_int(timetable.arrival_time),
                    )
                )

                # Filter stations for this route and add to global list
                timetable_station = StationM.objects.filter(
                    station_id=timetable.station.station_id
                ).first()

                if timetable_station.station_id not in sim_stations.keys():
                    new_station = Station(
                        env,
                        timetable_station.station_id,
                        timetable_station.name,
                        (timetable_station.lat, timetable_station.long),
                        1,
                        env_start,
                    )
                    sim_stations[timetable_station.station_id] = new_station
                    if new_station.id not in route_stations.keys():
                        route_stations[timetable_station.station_id] = new_station
                else:
                    if new_station.id not in route_stations.keys():
                        route_stations[timetable_station.station_id] = sim_stations[
                            timetable_station.station_id
                        ]

            new_trip = Trip(sim_timetables)

            if new_trip not in sim_trips:
                sim_trips.append(new_trip)
            route_trips.append(new_trip)

        new_route = BusRoute(
            env,
            env_start,
            route.route_id,
            route.name,
            [route for route in route_stations.values()],
            route_trips,
        )

        if route.route_id in sim_routes.keys():
            print("***ERROR*** Duplicate route id")
        else:
            sim_routes[route.route_id] = new_route

    # Create walks
    walks_from_stops = {}
    for walk_id in walks:
        if walk_id not in sim_routes:
            stops = [
                sim_stations[walks[walk_id][0]],
                sim_stations[walks[walk_id][1]],
            ]
            walk = Walk(env, env_start, walk_id, stops, 0, [])
            walks_from_stops[(walks[walk_id][0], walks[walk_id][1])] = walk
            #  sim_routes[walk_id] = walk  # TODO: Add walks to routes

    sim_itineraries = []
    for itinerary in itineraries:
        routes = []
        for route in itinerary["routes"]:
            if route["route_id"] != "walk":
                routes.append(
                    (
                        sim_routes[route["route_id"]],
                        sim_stations[route_ids[route["route_id"]]],
                    )
                )
            else:
                walk = walks_from_stops[(route["start"], route["end"])]
                routes.append((walk, sim_stations[walks[walk.id][1]]))

        new_itin = Itinerary(
            env,
            itinerary["itinerary_id"],
            routes,
        )

        sim_itineraries.append(new_itin)
        ITINERARIES.append(new_itin)
        new_itin.routes[0][0].first_stop.itin = ITINERARIES.index(
            new_itin
        )  # Assign itin index to station

    suburbs_db = StationM.objects.order_by().values("suburb").distinct()

    suburb_names = [suburb["suburb"] for suburb in suburbs_db.values()]
    list_set = set(suburb_names)
    suburb_names = list(list_set)
    suburbs_out = []
    for sub_name in suburb_names:
        # Create suburb for each
        average_suburb_pop = 100  # Very rough average
        distribute_frequency = 5
        max_distributes = 0
        stations_in_suburb = StationM.objects.order_by().filter(suburb=sub_name)
        active_stations_in_suburb_id = [
            station["station_id"]
            for station in StationM.objects.order_by()
            .filter(suburb=sub_name, station_id__in=active_stations)
            .values()
        ]
        active_stations_in_suburb = []
        for id in active_stations_in_suburb_id:
            active_stations_in_suburb.append(sim_stations[id])
        stations = [station["station_id"] for station in stations_in_suburb.values()]
        num_stations = len(active_stations_in_suburb)
        pop_distribution = {}
        active = sub_name in active_suburbs
        for (
            station
        ) in (
            active_stations_in_suburb
        ):  # Will need some changes when proper user input changed.
            pop_distribution[station] = (
                1 / num_stations
            ) * 100  # Currently evenly assign to all stations...
        suburb = Suburb(
            env,
            sub_name,
            pop_distribution,  # Distribution across stations
            stations,  # Station ids in suburb
            average_suburb_pop,  # Population
            distribute_frequency,  # Freq
            max_distributes,  # Max distributes
            active,
            env_start,
        )
        suburbs_out.append(suburb)

    stations_out = [station for station in sim_stations.values()]
    trips_out = sim_trips
    routes_out = [route for route in sim_routes.values()]
    itineraries_out = sim_itineraries

    return stations_out, trips_out, routes_out, itineraries_out, suburbs_out


def load_sim_data_into_db(
    stations: list[Station],
    routes: list[Route],
    itineraries: list[Itinerary],
    sim_id: int,
) -> None:
    """
    Generate all the data for the simulation and load it into the database (convert to SimStation,
    SimRoute, SimItinerary objects), then using these generation SimOutput object.
    """

    sim_output, created = SimulationOutput.objects.get_or_create(simulation_id=sim_id)

    if not created:
        print(f"Simulation #{sim_id} already exists in database, skipping save...")
        return

    # Create Stations
    for station in stations:
        for time, num_people in station.people_over_time.items():
            passenger_changes = PassengerChanges.objects.create(
                sim_id=sim_output,
                time=time,
                passenger_count=num_people,
            )

            passenger_changes.save()

            station_sim = StationSim.objects.create(
                station_id=station.id,
                sim_id=sim_output,
                name=station.name,
                lat=station.pos[0],
                long=station.pos[1],
                passenger_count=PassengerChanges.objects.order_by(
                    "-passenger_changes_id"
                ).first(),
            )

            station_sim.save()

    # Create Routes
    for route in routes:
        for station in route.stops:
            for bus in route.buses:
                for stop_name, time in bus.bus_time_log.items():
                    for time, passenger_count in bus.bus_passenger_changes.items():
                        bus_time_out = BusTimeOut.objects.create(
                            sim_id=sim_output,
                            stop_name=stop_name,
                            time=time,
                        )
                        bus_time_out.save()

                        passenger_changes = PassengerChanges.objects.create(
                            sim_id=sim_output,
                            time=time,
                            passenger_count=passenger_count,
                        )
                        passenger_changes.save()

                        bus_on_route = BusOnRouteInfo.objects.create(
                            bus_id=bus.id,
                            sim_id=sim_output,
                            bus_timeout=BusTimeOut.objects.order_by(
                                "-bustimeout_id"
                            ).first(),
                            bus_passenger_changes=PassengerChanges.objects.order_by(
                                "-passenger_changes_id"
                            ).first(),
                        )
                        bus_on_route.save()

                        route_sim = RouteSim.objects.create(
                            route_id=route.id,
                            sim_id=sim_output,
                            method=route.get_type(),
                            buses_on_route=BusOnRouteInfo.objects.order_by(
                                "-bus_id"
                            ).first(),
                            stations=StationSim.objects.filter(
                                sim_id=sim_output, name=station.name
                            ).first(),
                        )
                        route_sim.save()

    # Create Itineraries

    for itinerary in itineraries:
        for route in itinerary.routes:
            itin = ItinerarySim.objects.create(
                itinerary_id=itinerary.id,
                sim_id=sim_output,
                routes=RouteSim.objects.order_by("-route_sim_id").first(),
            )

            itin.save()


def generate_itins(user_data: dict) -> dict:
    """
    Collects itineraries for given user input data and returns them in the required format for running simulations
    Warning: This will call the TripGo API in bulk
    """
    # format user data how we need it
    end_time = convert_epoch(
        user_data["env_start"] + user_data["time_horizon"], user_data["snapshot_date"]
    )
    start_time = convert_epoch(user_data["env_start"], user_data["snapshot_date"])
    active_stations = user_data["active_stations"]
    print(
        f"Generating itineraries for {active_stations} at start time {start_time} and end time {end_time}"
    )

    # todo: move environment variables
    modes = ["pt_pub_bus"]
    api = "https://api.tripgo.com/v1/routing.json"
    key = "2286d1ca160dd724a3da27802c7aba91"
    endStation = "(-27.4979739, 153.0111389)\"UQ Chancellor's Place, zone D"
    num_itins = 3

    itin_id = 0
    itins_collected = []
    # collect itineraries for each active station
    for station in active_stations:
        parameters = {
            "v": "11",
            "from": f'({station["lat"]}, {station["long"]})',
            "to": endStation,
            "modes": modes,
            "bestOnly": "true",
            "includeStops": "false",
            "departAfter": start_time,
            "arriveBefore": end_time,
        }
        headers = {"X-TripGo-Key": key}
        data = callTripGoAPI(api, parameters, headers)
        # print(data)
        format_data = formatItins(
            data, num_itins, station["station_id"].zfill(6), itin_id
        )
        itins_collected += format_data
        itin_id += num_itins
    print("itins ", itins_collected)
    return itins_collected


def convert_epoch(time: int, date_str: str) -> int:
    """
    converts a given time in seconds from midnight and a date string of format "yyyy--mm-dd"
    to seconds since 1970
    """
    epoch_date = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
    epoch_time = epoch_date + time
    return epoch_time


def does_contain(itin, itins):
    for i in itins:
        if i["routes"] == itin["routes"]:
            return True
    return False


def formatItins(response, num_itins, start_station_id, start_itin_id):
    """
    Formats itineraries from response of a single api call
    """
    itins = []
    itin_id = start_itin_id
    for group in response["groups"]:
        options = group["trips"]
        options = sorted(options, key=lambda k: k["weightedScore"])
        trips_parsed = 0
        for trip in options:
            exit = False
            routes = []
            count = 0
            for segment in trip["segments"]:
                # Want to find bus/walk route
                hash = segment["segmentTemplateHashCode"]
                # Now find associated segmentTemplate
                template = None
                for segTemp in response["segmentTemplates"]:
                    if segTemp["hashCode"] == hash:
                        template = segTemp
                        break
                route_id = ""
                if "WALK" in template["action"].upper():
                    route_id = "walk"
                elif "TAKE" in template["action"].upper():
                    route_id = segment["routeID"]

                # Now want to get from where to where
                from_station = template["from"]["stopCode"]
                if count == 0 and from_station != start_station_id:
                    # Coords where too close to another stop and it tried to make that the start
                    exit = True  # for double break
                    break
                to_station = template["to"]["stopCode"]
                route = {"route_id": route_id, "start": from_station, "end": to_station}
                count += 1
                routes.append(route)
            if exit:
                exit = False
                continue
            itin = {"itinerary_id": itin_id, "routes": routes}
            if not does_contain(itin, itins):
                itin_id += 1
                trips_parsed += 1
                itins.append(itin)
                if trips_parsed >= num_itins:
                    break
    return itins


def callTripGoAPI(api, parameters, headers):
    """
    Calls the TripGoAPI and returns the response
    """
    response = requests.get(api, params=parameters, headers=headers)
    if response.status_code == 200:
        print("sucessfully fetched TripGo data")
        return response.json()
    else:
        return f"failed to fetch TripGo data: {response.status_code}"
