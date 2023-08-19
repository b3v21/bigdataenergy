import itertools
import random
from simpy import Environment, Resource
import math

PERSON_BOARD_TIME = 0.1


class People:
    """
    A group of people which will travel along a route.
    """

    def __init__(self, env: Environment, num_people: int, start_time: int) -> None:
        self.env = env
        self.num_people = num_people
        self.start_time = start_time
        self.start_location = None

    def get_num_people(self) -> int:
        return self.num_people

    def add_start_loc(self, location: tuple[int, int]) -> None:
        self.start_location = location

    def get_num_people(self) -> int:
        return self.num_people

    def change_num_people(self, change: int) -> None:
        self.num_people += change

    def get_start_time(self) -> int:
        return self.start_time


class BusStop:
    """
    Each BusStop object contains a SimPy Resource which represents the number of bus
    bays available at the stop. Also a list of People objects representing the people
    waiting at the bus stop is stored.
    """

    def __init__(
        self,
        env: Environment,
        name: str,
        pos: tuple[int, int],
        bays: int,
        people: list[People],
        bus_spawn_max: int = 0,
        timing: int = None,
    ) -> None:
        self.bays = Resource(env, capacity=bays)
        self.people = people
        self.name = name
        self.pos = pos
        self.timing = timing
        self.buses_spawned = 0
        self.bus_spawn_max = bus_spawn_max
        self.env = env

    def num_people(self) -> int:
        return sum([p.get_num_people() for p in self.people])

    def add_people(self, new_people: People) -> None:
        self.people.append(new_people)

    def put(self, passengers: int) -> None:
        self.people += passengers

    def board_bus(self, num_people_to_board: int) -> list[People]:
        """
        Given the number of people who are at the stop, this method returns a list
        'people_to_get' containing the people which a bus can collect from this stop.
        """

        current_index = 0
        boarded = 0
        people_to_get = []

        while boarded != num_people_to_board:
            group_of_people = self.people[current_index]

            if group_of_people.get_num_people() >= num_people_to_board:
                group_of_people.add_start_loc(self.pos)

                # If whole group is collected, add to bus and remove from stop
                people_to_get.append(group_of_people)
                self.people.remove(group_of_people)

                if group_of_people.get_num_people() == num_people_to_board:
                    return people_to_get

                else:
                    boarded += group_of_people.get_num_people()
                    current_index += 1
                    continue
            else:
                # If portion is collected, create new people that get on bus and edit size
                # of old people
                new_people = People(
                    self.env,
                    group_of_people.get_num_people(),
                    self.people[current_index].get_start_time(),
                )
                new_people.add_start_loc(self.pos)
                people_to_get.append(new_people)

                self.people[current_index] -= group_of_people.get_num_people()

                return people_to_get


class BusRoute:
    """
    Object to store series of routes, needs to spawn the initial stops bus spawn process.
    """

    def __init__(self, env: Environment, name: str, stops: list[BusStop]) -> None:
        self.name = name
        self.stops = stops
        self.first_stop = stops[0]
        self.last_stop = stops[-1]
        self.env = env
        self.running = self.env.process(self.initiate())

    def initiate(self) -> None:
        """
        A function to initiate the route. Will spawn busses on the accoridng time
        intervals.
        """

        while self.first_stop.buses_spawned != self.first_stop.bus_spawn_max:
            if self.env.now % self.first_stop.timing == 0:
                self.first_stop.buses_spawned += 1
                name = f"B{self.first_stop.buses_spawned}_{self.name}"
                self.env.process(Bus(self.env, name, self).start_driving())
                print(f"({self.env.now}): Bus {name} is starting on route {self.name}")
            yield self.env.timeout(1)


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
        route: BusRoute,
        location_index: int = 0,
        capacity: int = 50,
    ) -> None:
        self.passengers = []  # Container for passengers on it
        self.name = name
        self.route = route
        self.capacity = capacity
        self.env = env
        self.location_index = location_index
        self.current_stop = self.route.stops[self.location_index].name

    def start_driving(self) -> None:
        """
        Logic of a bus:
        When spawned --> Pick up people from current stop
        When full OR no more people --> Go to final stop OR go to next stop
        Repeat

        """
        while True:
            print(
                f"({self.env.now}): Bus {self.name} is arriving stop {self.current_stop}"
            )
            with self.route.stops[self.location_index].bays.request() as req:
                yield req
                if self.route.stops[(self.location_index)] != self.route.last_stop:
                    yield self.env.process(self.load_passengers())
                else:
                    yield self.env.process(self.deload_passengers())

                next = (self.location_index + 1) % len(self.route.stops)
            print(
                f"({self.env.now}): Bus {self.name} is leaving from stop {self.current_stop} to go to {self.route.stops[next].name}"
            )
            time_to_travel = distance_between(
                self.route.stops[self.location_index], self.route.stops[next]
            )
            self.location_index = next
            yield self.env.timeout(time_to_travel)

    def load_passengers(self) -> None:
        """Load passengers from the current stop onto this bus."""

        bus_seats_left = self.capacity - self.passenger_count()
        people_at_stop = sum(
            group.get_num_people()
            for group in self.route.stops[self.location_index].people
        )

        if not people_at_stop:
            print(f"({self.env.now}): No passengers at stop {self.name}")
            return

        if not bus_seats_left:
            print(f"({self.env.now}): No seats left on bus {self.name}")
            # add functionality in here
            return

        people_to_ride = self.route.stops[self.location_index].board_bus(
            min(people_at_stop, bus_seats_left)
        )

        num_people_to_board = sum([p.get_num_people() for p in people_to_ride])
        load_time = num_people_to_board * PERSON_BOARD_TIME
        self.passengers += people_to_ride

        yield self.env.timeout(load_time)
        print(
            f"({self.env.now}): Bus {self.name} has loaded {num_people_to_board} people from {self.current_stop}"
        )

    def deload_passengers(self) -> None:
        # Currently all passengers get off...
        get_off = self.passenger_count()

        if not get_off:
            print(f"({self.env.now}): No passengers got off the bus {self.name}")
            return

        self.route.stops[self.location_index].put(self.passengers)
        self.passengers.clear()
        off_time = get_off * PERSON_BOARD_TIME
        yield self.env.timeout(off_time)
        print(
            f"({self.env.now}): Bus {self.name} has dropped off {get_off} people at {self.current_stop}"
        )

    def passenger_count(self) -> int:
        return sum(group.get_num_people() for group in self.passengers)


def distance_between(stop1: BusStop, stop2: BusStop) -> int:
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

    cultural_centre_bus_station = BusStop(
        env, "Cultural Centre Station", (0, 0), 1, [group1], 10, 2
    )
    king_george_square_bus_station = BusStop(
        env, "King George Square Bus Station", (0, 3), 2, [group2]
    )
    roma_street_busway_station = BusStop(
        env, "Roma Street Busway Station", (0, 5), 3, [group3]
    )
    given_tce_bus_stop = BusStop(env, "Given Tce Bus Stop", (0, 7), 1, [group4])

    BusRoute(
        env,
        "385",
        [
            cultural_centre_bus_station,
            king_george_square_bus_station,
            roma_street_busway_station,
            given_tce_bus_stop,
        ],
    )
    BusRoute(
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


def simple_example() -> None:
    env = Environment()

    group1 = People(env, 15, 0)

    first_stop = BusStop(env, "first_stop", (0, 0), 1, [group1], 1, 1)
    last_stop = BusStop(env, "last_stop", (2, 2), 1, [], 3)

    BusRoute(env, "the_route", [first_stop, last_stop])
    env.run(10)


if __name__ == "__main__":
    simple_example()
