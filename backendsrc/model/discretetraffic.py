import itertools
import random
from simpy import Environment, Resource
import math

PERSON_BOARD_TIME = 0.1


class People:
    def __init__(self, env: Environment, count: int, start_time: int) -> None:
        self.env = env
        self.count = count
        self.start_time = start_time
        self.start_location = None

    def get_count(self) -> int:
        return self.count

    def add_start_loc(self, location: tuple[int, int]) -> None:
        self.start_location = location

    def change_count(self, change: int) -> None:
        self.count += change

    def get_start_time(self) -> int:
        return self.start_time


class BusStop:
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
        self.bays = Resource(
            env, capacity=bays
        )  # Numbers of spots the bus can pull into at the stop
        self.people = people
        self.name = name
        self.pos = pos
        self.timing = timing
        self.buses_spawned = 0
        self.bus_spawn_max = bus_spawn_max
        self.env = env

    # For adding more groups of people to stops (if more rock up at a different time)
    def add_people(self, new_people: People) -> None:
        self.people.append(new_people)

    def get(self, amount: int) -> list[People]:
        """
        Given an amount, this method returns a list 'people_to_get' containing the people
        which a bus can collect from this stop.
        """

        current_index = 0
        amount_removed = 0
        people_to_get = []

        while amount_removed != amount:
            removable = min(amount, self.people[current_index].get_count())

            if self.people[current_index].get_count() - removable == 0:
                # If whole group is collected, add to bus and remove from stop
                people_to_get.append(self.people[current_index])

                self.people[current_index].add_start_loc(self.pos)
                self.people.remove(self.people[current_index])

                if removable == amount:
                    return people_to_get

                else:
                    amount_removed += removable
                    current_index += 1
                    continue

            else:
                # If portion is collected, create new people that get on bus and edit size
                # of old people
                new_people = People(
                    self.env, removable, self.people[current_index].get_start_time()
                )
                new_people.add_start_loc(self.pos)

                people_to_get.append(new_people)
                self.people[current_index].change_count(-removable)

                return people_to_get

    def put(self, passengers: int) -> None:
        self.people += passengers


class BusRoute:
    """
    Object to store series of routes, needs to spawn the initial stops bus spawn process.
    """

    def __init__(self, env: Environment, name: str, stops: list[BusStop]) -> None:
        self.name = name
        self.stops = stops
        self.start = stops[0]
        self.end = stops[-1]
        self.env = env
        self.running = self.env.process(self.initiate())

    def initiate(self) -> None:
        """
        A function to initiate the route. Will spawn busses on the accoridng time intervals.
        """
        first_stop = self.start
        while first_stop.buses_spawned != first_stop.bus_spawn_max:
            if self.env.now % first_stop.timing == 0:
                # Spawn a bus out of thin air
                first_stop.buses_spawned += 1
                name = f"B{first_stop.buses_spawned}_{self.name}"
                self.env.process(
                    Bus(self.env, name, self).start()
                )  # Start bus running process after initiating the object
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

    def start(self) -> None:
        """
        Logic of a bus:
        When spawned --> Pick up people from current stop
        When full OR no more people --> Go to final stop OR go to next stop
        Repeat

        """
        while True:
            current_stop = self.route.stops[self.location_index].name

            print(f"({self.env.now}): Bus {self.name} is arriving stop {current_stop}")
            with self.route.stops[
                self.location_index
            ].bays.request() as req:  # Request to get on of the "stops" at the bus stop
                yield req  # Make sure wait till bay is available
                if self.route.stops[(self.location_index)] != self.route.end:
                    yield self.env.process(self.load_passengers())
                else:
                    yield self.env.process(self.deload_passengers())

                next = (self.location_index + 1) % len(
                    self.route.stops
                )  # Update moving to next
            print(
                f"({self.env.now}): Bus {self.name} is leaving from stop {current_stop} to go to {self.route.stops[next].name}"
            )
            time_to_travel = distance_between(
                self.route.stops[self.location_index], self.route.stops[next]
            )
            self.location_index = next
            yield self.env.timeout(time_to_travel)

    def load_passengers(self) -> None:
        current_stop = self.route.stops[self.location_index].name

        can_load = self.capacity - self.passenger_count()
        will_load = min(
            can_load,
            sum(
                group.get_count()
                for group in self.route.stops[self.location_index].people
            ),
        )

        if not will_load:
            print(f"({self.env.now}): No passengers getting on the bus {self.name}")
            return

        # Get as many passengers as possible from the stop
        self.passengers += self.route.stops[self.location_index].get(will_load)
        load_time = will_load * PERSON_BOARD_TIME
        yield self.env.timeout(load_time)  # Timeout till time passed
        print(
            f"({self.env.now}): Bus {self.name} has loaded {will_load} people from {current_stop}"
        )

    def deload_passengers(self) -> None:
        current_stop = self.route.stops[self.location_index].name

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
            f"({self.env.now}): Bus {self.name} has dropped off {get_off} people at {current_stop}"
        )

    def passenger_count(self) -> int:
        return sum(group.get_count() for group in self.passengers)


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
