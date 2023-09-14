from __future__ import annotations
from simpy import Environment, Resource
from abc import ABC, abstractmethod
from random import randint, randrange, choice
from pathlib import Path
from math import ceil, floor
import django
import os
import sys
import copy
from datetime import time


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
)  # noqa: E402


START_TIME = 840
TIME_HORIZON = 15
PERSON_BOARD_TIME = 0.1
MINUTES_IN_DAY = 1440

# THIS IS FOR STORING ITINERARY OBJECTS PRODUCED BY THE SIM
ITINERARIES = []


def convert_date_to_int(time: time) -> int:
    return time.hour * 60 + time.minute


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

    def log(self, where: tuple[str, int]) -> None:
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
        id: str,
        name: str,
        pos: tuple[float, float],
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
                split.people_log = copy.deepcopy(people.people_log)
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
            if (not ITINERARIES[group.itinerary_index].last_leg(group) 
                and (ITINERARIES[group.itinerary_index].get_current(group)[1] == self 
                     or  ITINERARIES[group.itinerary_index].get_current_route(group).last_stop == self)):
                #At current last part of their itin
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
                    .get_current_route(group)
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
            print(
                f"({self.env.now+self.env_start}): No passengers at stop {station.name}"
            )
            return

        if not seats_left:
            print(
                f"({self.env.now+self.env_start}): No seats left on bus {self.get_name()}"
            )
            return

        people_to_ride = station.board(min(people_at_stop, seats_left), self.route)

        num_people_to_board = sum([p.get_num_people() for p in people_to_ride])
        load_time = int(num_people_to_board * PERSON_BOARD_TIME)
        self.people += people_to_ride

        yield self.env.timeout(load_time)
        for people in people_to_ride:
            people.log((self.name, self.id))
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
        # Currently all passengers get off...
        get_off_list = []
        if self.route.last_stop == station:
            # Everyone left needs to get off
            get_off_list = self.people
        else:
            # Only those who want to get off should get off
            get_off_list = self.get_people_deloading(station)

        get_off = 0
        if get_off_list != None:
            for people in get_off_list:
                get_off += people.get_num_people()
        else:
            get_off = None

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

        station.put(get_off_list)

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

                    yield self.env.process(
                        self.deload_passengers(bus_route.get_current_stop(self))
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
                cur_stop = bus_route.get_current_stop(self)
                travel_time = 0
                for stop, time in self.trip.timetable:
                    if cur_stop.name == stop:
                        travel_time = time - (self.env.now + self.env_start)
                if travel_time <= 0:
                    print(
                        "***ERROR*** Travel time <= 0 due to current implementation of trip, forcing 1"
                    )
                    travel_time = 1

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
            station_info = None
            trip_info = None
            trips_inited = []
            for trip in trips_to_iniate:
                for station, arrival_time in trip.timetable:
                    if arrival_time == (self.env.now + self.env_start):
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
                        self.bus_time_log.append({})
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
            if (self.env.now + self.env_start) % self.frequency == 0:
                num_people = randint(0, self.population)
                # have_distributed = self.distribute_people(num_people)
                have_distributed = self.distribute_people(
                    ceil(self.population / (self.max_distributes))
                )  # Do this num generation better

                current_distribution += 1
                self.population -= have_distributed
            yield self.env.timeout(1)

        # distribute remaining people if there are any
        if self.population > 0:
            _ = self.distribute_people(self.population)

    def distribute_people(self, num_people: int) -> int:
        """
        TODO: This will be replaced with a standard form of distribution + the
        possibility for user inputs via the frontend.

        Currently just randomly selects itinerary -> randomly selects route on itinerary
        -> randomly selects station on route and drops a percentage of num_people at that
        station based off the self.station_distribution dict.
        """
        people_distributed = 0
        while people_distributed != num_people:
            # Pick a itin to distribute to
            itin = choice(self.itineraries)

            # Pick a route from it to distribute to
            route_tuple = choice(itin.routes)
            route = route_tuple[0]

            possible_stations = list(
                set(self.station_distribution.keys()) & set(route.stops)
            )

            if not possible_stations:
                continue
            station = choice(possible_stations)
            if not self.station_distribution[station]:
                continue

            num_for_stop = ceil(self.station_distribution[station] / 100 * num_people)

            if num_for_stop > num_people - people_distributed:
                num_for_stop = num_people - people_distributed

            people_arriving_at_stop = People(
                env=self.env,
                count=num_for_stop,
                start_time=self.env.now,
                start_location=station,
                itinerary_index=self.itineraries.index(itin),
                current_route_in_itin_index=itin.routes.index(route_tuple),
                env_start=self.env_start,
            )

            station.put([people_arriving_at_stop], from_suburb=True)

            print(
                f"({self.env.now+self.env_start}): {num_for_stop} people arrived at {station.name} in {self.name}"
            )

            people_distributed += num_for_stop
        return people_distributed


class Trip:
    """This trip object will be created to hold transporter timings"""

    def __init__(self, timetable: list[tuple[str, int]]) -> None:
        self.timetable = timetable


def run_simulation(user_data: dict[dict], sim_id: int) -> dict[dict]:
    """Main function to run the simulation"""

    env = Environment()

    stations, trips, routes, itineraries = get_data(
        env,
        user_data["env_start"],
        user_data["time_horizon"],
        user_data["itineraries"],
        user_data["service_ids"],
    )

    print(f"Models successfully created for simulation #{sim_id}.")
    for itin in itineraries:
        print(itin)
        print(itin.routes)
        print()
    print()

    suburb = Suburb(
        env=env,
        name="Simple Suburb",
        station_distribution={stations[0]: 100, stations[1]: 0},
        population=200,
        frequency=10,
        max_distributes=0,
        itineraries=[itineraries[0]],
        env_start=user_data["env_start"],
    )

    env.run(user_data["time_horizon"])
    print(f"Simulation #{sim_id} successfully ran.")

    return process_simulation_output(stations, trips, routes, itineraries)


def process_simulation_output(
    stations: list[Station],
    trips: list[Trip],
    routes: list[Route],
    itineraries: list[Itinerary],
) -> dict[dict]:
    """
    Analyse all the models once the simulation has finished running and returns the
    information which will be sent to the frontend. Some information requested from the
    frontend is as follows...

    Routes:
    - occupancy of the route at each point (station) of the journey

    Stops
    - Average wait times at stations
    - Time taken to get to the destination from the starting station (for each group of people?)

    - Distance from event

    Itinerary
    - Time taken at each step (walking, bus etc)
    - Also will probably need to send some information about routes directly.
      I think at the moment route data is just contained in the itinerary?
    """

    output = {"Routes": {}, "Stations": {}, "Itineraries": {}}

    for route in routes:
        output["Routes"][route.id] = {}
        rd = output["Routes"][route.id]
        rd["method"] = route.get_type()
        if route.get_type() == "BusRoute":
            rd["Timeout"] = route.bus_time_log
            rd["Popout"] = route.bus_pop_log
        elif route.get_type() == "Walk":
            rd["Walkout"] = route.walk_time_log

        rd["stations"] = {}
        for station in route.stops:
            rd["stations"][station.id] = {}
            sd = rd["stations"][station.id]
            sd["station_name"] = station.name
            sd["pos"] = {
                "lat": station.pos[0],
                "long": station.pos[1],
            }

    for station in stations:
        output["Stations"][station.id] = {}
        sd = output["Stations"][station.id]
        sd["station_name"] = station.name
        sd["pos"] = {
            "lat": station.pos[0],
            "long": station.pos[1],
        }
        sd["station_out"] = station.people_over_time

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
                
    return output


def get_data(
    env: Environment,
    env_start: int,
    time_horizon: int,
    itineraries: list,
    service_ids: list[str],
) -> tuple[dict[int, Station], list[Trip], dict[int, Route], list[Itinerary]]:
    """
    This function accesses the data from the database and converts it into simulation
    objects.
    """

    # Itineraries need to be generated elsewhere and converted here into
    # Itinerary objects, for now just use placeholder which is a list of routes
    # that the itinerary use

    # Get all calendar objects (containing service info) that run on a Friday
    calendars = CalendarM.objects.all().filter(service_id__in=service_ids)

    # Get all routes that are used in the itineraries
    route_ids = {}
    
    for itinerary_id, itinerary in itineraries.items():
        for route in itinerary:
            route_id = route['route_id']
            start = route['start']
            end = route['end']

            if route_id != "walk":
                route_ids[route_id] = end
            

    db_routes = RouteM.objects.all().filter(route_id__in=list(route_ids.keys()))

    sim_routes = {}
    sim_trips = []
    sim_stations = {}

    for route in db_routes:
        # Get trip_ids that run on a Friday for this particular route
        db_trips = TripM.objects.all().filter(service_id__in=calendars, route_id=route)

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

    sim_itineraries = []
    for itinerary_id, itinerary in itineraries.items():
        new_itin = Itinerary(
            env,
            env_start,
            [
                (sim_routes[route["route_id"]], sim_stations[route_ids[route["route_id"]]])
                for route in itinerary
            ],
        )
        sim_itineraries.append(new_itin)
        ITINERARIES.append(new_itin)

    stations_out = [station for station in sim_stations.values()]
    trips_out = sim_trips
    routes_out = [route for route in sim_routes.values()]
    itineraries_out = sim_itineraries

    return stations_out, trips_out, routes_out, itineraries_out
