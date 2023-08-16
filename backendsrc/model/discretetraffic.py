import itertools
import random
import simpy
import math

PERSON_BOARD_TIME = 0.1

class BusStop:
    def __init__(self, env, name, pos, stops, people, capacity, timing=None, bus_spawn_max=0):
        self.stops = simpy.Resource(env, capacity=stops)
        self.people = simpy.Container(env, init=people, capacity=capacity)
        self.name = name
        self.pos = pos
        self.timing = timing
        self.buses_spawned = 0
        self.bus_spawn_max = bus_spawn_max
        self.env = env
            
        #self.mon_proc = env.process(self.monitor_tank(env))

    
    


    """
    Would include this monitor process if we want to simulate people coming into the stop after other people have been taken
    def monitor_tank(self, env):
        while True:
            if self.gas_tank.level < 100:
                print(f'Calling tanker at {env.now}')
                env.process(tanker(env, self))
            yield env.timeout(15)
   

def tanker(env, gas_station):
    yield env.timeout(10)  # Need 10 Minutes to arrive
    print(f'Tanker arriving at {env.now}')
    amount = gas_station.gas_tank.capacity - gas_station.gas_tank.level
    yield gas_station.gas_tank.put(amount)
    """

class BusRoute:
    """
    Object to store series of routes, needs to spawn the initial stops bus spawn process.
    """

    def __init__(self, env, name, stops):
        self.name = name
        self.stops = stops
        self.start = stops[0]
        self.end = stops[-1]
        self.env = env
        #self.start.bus_spawn(self)
        #self.start.bus_proc = self.env.process(self.start.bus_spawn(self))
        self.running = self.env.process(self.initiate())

    def initiate(self):
        stop = self.start
        while True:
            if stop.buses_spawned == stop.bus_spawn_max:
                break
            if self.env.now % stop.timing == 0:
                #Spawn a bus lol
                stop.buses_spawned += 1
                name = f'B{stop.buses_spawned}_{self.name}'
                self.env.process(Bus(self.env, name, self).bus())
                print(f'({self.env.now}): Bus {name} is starting on route {self.name}')
            yield self.env.timeout(1)
                #bus.bus()

class Bus:
    """
    A bus arrives at the bus stop for picking up people.

    It requests one of the bus stops stops pumps and tries to get the
    desired amount of people from it. 
    
    If the stop is emptied, it will leave.
    """
    def __init__(self, env, name, route, location_index=0, passengers=0, capacity=50):
        self.passengers = simpy.Container(env, init=passengers, capacity=capacity)
        self.name = name
        self.route = route
        self.env = env
        self.location = location_index
        
        #Now add the object to the simulation with its actions
        #self.env.process(self.bus())


    def bus(self):
        """
        Logic of a bus:
        When spawned --> Pick up people from current stop
        When full OR no more people --> Go to final stop OR go to next stop
        Repeat

        """
        while True:
            print(f'({self.env.now}): Bus {self.name} is arriving stop {self.route.stops[self.location].name}')
            #Load people
            with self.route.stops[self.location].stops.request() as req:
                if self.route.stops[(self.location)] != self.route.end:
                    print(f'({self.env.now}): Bus {self.name} is loading people from stop {self.route.stops[self.location].name}')
                    can_load = self.passengers.capacity - self.passengers.level
                    will_load = min(can_load, self.route.stops[self.location].people.level)
                    if (will_load != 0):
                        yield self.route.stops[self.location].people.get(will_load) #Can I do this without the yield? :shrug: --> May cause issues if two buses "getting" people from same stop at the same time, bus people dont regen?
                        yield self.passengers.put(will_load)
                        load_time = will_load * PERSON_BOARD_TIME
                        yield self.env.timeout(load_time) ##########
                        print(f'({self.env.now}): Bus {self.name} has loaded {will_load} people from {self.route.stops[self.location].name}')
                else:
                    print(f'({self.env.now}): Bus {self.name} is dropping people off at {self.route.stops[self.location].name}')
                    get_off = self.passengers.level
                    yield self.route.stops[self.location].people.put(get_off) #YIELD?
                    yield self.passengers.get(get_off)
                    off_time = get_off * PERSON_BOARD_TIME
                    yield self.env.timeout(off_time)
                    print(f'({self.env.now}): Bus {self.name} has dropped off {get_off} people at {self.route.stops[self.location].name}')

                next = (self.location + 1)%len(self.route.stops) #Update moving to next
                print(f'({self.env.now}): Bus {self.name} is leaving from stop {self.route.stops[self.location].name} to go to {self.route.stops[next].name}')
                time_to_travel = distance_between(self.route.stops[self.location], self.route.stops[next])
                self.location = next
                yield self.env.timeout(time_to_travel)

def distance_between(stop1, stop2):
    #This may be based off of calculation or database of data, effectively, return the time it takes to travel between two locations
    dist = math.sqrt(math.pow((stop1.pos[0] - stop2.pos[0]),2) + math.pow((stop1.pos[1] - stop2.pos[1]),2))
    BUSY_LEVEL = 1 #TEMP ----------------------------------------------------
    time = math.floor(dist * BUSY_LEVEL)
    return time

######################################################################################################

env = simpy.Environment()

### Create Stuff ###
# Manual Atm, will change to based off input or something 

cultural_centre_bus_station = BusStop(env, "Cultural Centre Station", (0,0), 4, 100, 400, 30, 2)
king_george_square_bus_station = BusStop(env, "King George Square Bus Station", (0, 3), 2, 100, 200)
roma_street_busway_station = BusStop(env, "Roma Street Busway Station", (0,5), 3, 100, 300)
given_tce_bus_stop = BusStop(env, "Given Tce Bus Stop", (0, 7), 1, 0, 1000)

bus_route_385 = BusRoute(env, "385", [cultural_centre_bus_station, king_george_square_bus_station, roma_street_busway_station, given_tce_bus_stop])

###--------------###

env.run(60)