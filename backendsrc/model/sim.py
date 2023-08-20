from __future__ import annotations
import itertools
import random
from simpy import Environment, Resource
import math


PERSON_BOARD_TIME = 0.1


class People:
    def __init__(self, env: Environment, count: int, start_time: int, start_location: BusStop) -> None:
        self.env = env
        self.count = count
        self.start_time = start_time
        self.start_location = start_location
        self.end_time = None
        self.travel_route = None #To come later

    def __str__(self) -> str:
        return f'Count: {self.count}, Start Time: {self.get_start_time()}, End Time: {self.get_end_time()}, Journey Time: {self.get_end_time() - self.get_start_time() if self.get_end_time() != None else "N/A"}, Start Loc: {self.start_location.name}'

    def get_count(self) -> int:
        return self.count

    def add_start_loc(self, location: BusStop) -> None: #Changed Location to busStop, for now
        self.start_location = location

    def change_count(self, change: int) -> None:
        self.count += change

    def get_start_time(self) -> float:
        return self.start_time
    
    def set_end_time(self, time: float) -> None:
        self.end_time = time

    def get_end_time(self) -> float:
        return self.end_time

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

    def __str__(self) -> str:
        output = f'{self.name}: Total People = {self.num_people()}, Total Groups = {len(self.people)}'
        for people in self.people:
            output += f'\n{str(people)}'
        return output


    # For adding more groups of people to stops (if more rock up at a different time)
    def add_people(self, new_people: People) -> None:
        self.people.append(new_people)

    def get(self, amount: int) -> list[People]:
        """
        Given an amount, this method returns a list 'people_to_get' containing the people
        which a bus can collect from this stop.
        """
        cur_total = 0
        people_to_get = []
        
        for people in self.people:
            if people.get_count() + cur_total > amount:
                #Would be adding too many people --> Split
                excess = (people.get_count() + cur_total) - amount
                split = People(self.env, excess, people.start_time, people.start_location)
                people.change_count(-excess)
                self.people.extend([split])
                people_to_get.append(people)
                break
            people_to_get.append(people)
            cur_total += people.get_count()
            if cur_total == amount:
                break
        return people_to_get
        
    def put(self, passengers: list[People]) -> None:
        for people in passengers:
            people.set_end_time(self.env.now)
        self.people.extend(passengers)

    def num_people(self) -> int:
        return sum([people.count for people in self.people])


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

                print(f'Bus has {self.passenger_count()}')
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
        self.passengers.extend(self.route.stops[self.location_index].get(will_load))
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

class Suburb:
    def __init__(self, 
                 env: Environment, 
                 name: str, 
                 bus_stops: dict[BusStop:float], 
                 population: int, 
                 frequency: int,
                 max_distributes: int):
        self.env = env
        self.name = name
        self.bus_stops = bus_stops #Dictionary of bustops and percentages of population to take
        self.population = population
        self.frequency = frequency #How often to try and distribute the population
        self.max_distributes = max_distributes

        #Start process
        self.pop_proc = self.env.process(self.suburb())

    def suburb(self):
        """
        Process for the existence of the suburb object.
        Every frequency minutes, will distribute random* amount of population to nearby suburbs.
        """
        distributes = 0

        while distributes <= self.max_distributes:
            if self.env.now % self.frequency == 0:
                #Distribute population
                to_dist = random.randint(0, self.population) if distributes < self.max_distributes else self.population
                have_distributed = 0
                for stop in self.bus_stops.keys(): #Will need to change when handling different stop types
                    num_for_stop = math.floor(self.bus_stops[stop]/100 * (to_dist-have_distributed))
                    if num_for_stop == 0:
                        continue
                    if stop == list(self.bus_stops.keys())[-1]: 
                        num_for_stop = to_dist - have_distributed #To account for rounding
                    stop.put([People(self.env, num_for_stop, self.env.now, stop)])
                    have_distributed += num_for_stop
                    if num_for_stop != 0:
                        print(f'({self.env.now}): {num_for_stop} new people have just arrived at {stop.name} in {self.name}')
            yield self.env.timeout(1)
    


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

    #group1 = People(env, 15, 0, first_stop)

    first_stop = BusStop(env, "first_stop", (0, 0), 1, [], 1, 1)
    last_stop = BusStop(env, "last_stop", (2, 2), 1, [], 3)

    simple_suburb = Suburb(env, "Simple Suburb", {first_stop:100, last_stop:0}, 100, 10, 4)

    BusRoute(env, "the_route", [first_stop, last_stop])
    env.run(60)
    print(first_stop)
    print(last_stop)


if __name__ == "__main__":
    simple_example()
