import queue, math
from datetime import datetime

"""
Assumptions:
    Everyone is only going to stadium
    Buses only going on stadium routes
    ~15 sec to get on and off
    Buses idle and buses there are different
"""



class Person:
    total_stadium = 0
    board_time = 0.25
    dict = {"A":[],"B":[],"C":[],"D":[],"E":[],"F":[],"G":[]}

    def __init__(self, location, start_time):
        self.location = location
        self.start = start_time

    def off(self):
        #print("I got off from ", self.location)
        Person.total_stadium += 1
        Person.dict[self.location].append(time - self.start)
        

class Bus:
    #Buses should also track their stats !!!
    all_buses = []

    def __init__(self, route, location_index, time_till_next_stop, capacity=50, status=None):
        self.route = route
        self.passengers = queue.Queue()
        self.location_index = location_index
        self.capacity = capacity
        self.status = status
        self.time_till_next_stop = time_till_next_stop
        Bus.all_buses.append(self)
    def tick_all():
        for i in Bus.all_buses:
            i.tick()

    def tick(self):
        if self.status == "Enroute":
            self.time_till_next_stop -= 1
            if self.time_till_next_stop < 0:
                #Still going
                pass
            else:
                #Arrived
                self.location_index = (self.location_index + 1)%len(self.route.locations)
                if self.location_index == 0:
                    #Have arrived back to start of the run
                    self.route.start_location.idle_bus.put(self)
                if (self.route.locations[self.location_index].bus_q.qsize() < self.route.locations[self.location_index].bus_max):
                    self.status = "At Stop"
                    self.route.locations[self.location_index].bus_q.put(self)
                    #Now wait to be handled by the stop itself          
            

class Route:
    all_routes = []
    busy = {"Normal":1, "Busy":1.2, "Quiet":0.8}

    def tick_all():
        for i in Route.all_routes:
            i.tick()

    def __init__(self, locations, timing, busy_level="Normal"):
        self.locations = locations
        self.busy_level = busy_level
        self.start_location = locations[0]
        self.end_location = locations[-1]
        self.timing = timing
        Route.all_routes.append(self)

    def tick(self):
        if time % self.timing == 0:
            #Start a bus on this route --> Maybe handle this differently. Need to think about all routes and such, objects may need to have incresed complexity.
            if self.start_location.idle_bus.qsize() != 0:
                self.start_location.start(self)
            #Handle if no buses --> Summon?


class BusStop:
    all_stops = []
    def tick_all():
        for i in BusStop.all_stops:
            i.tick()
    def __init__(self, name, position, people, bus_max, idle_buses=0):
        self.name = name
        self.position = position
        self.people = people
        self.bus_max = bus_max
        self.bus_q = queue.Queue()
        self.idle_bus = queue.Queue()
        for i in range(0, idle_buses):
            self.idle_bus.put(Bus(None, 0, 0))
        
        BusStop.all_stops.append(self)
    
    def start(self, route):
        bus = self.idle_bus.get()
        bus.route = route
        bus.status = "At Stop"
        self.bus_q.put(bus)

    def tick(self):
        buses_left = 0 #Variable to account for change in indexing of queue if bus finished and removed from Q
        for i in range(0, min(self.bus_max, self.bus_q.qsize())): 
            if self.bus_q.qsize() != 0:
                #Bus here, either load or let off people
                bus = self.bus_q.queue[i - buses_left]
                if self.name == bus.route.end_location.name:
                    #At final, people get off
                    for i in range(0, min(int(1/Person.board_time), bus.passengers.qsize())):
                        if bus.passengers.qsize() == 0:
                            #Send bus back
                            break
                        #Passengers Getting off the bus
                        dqer = bus.passengers.get() #Remove Bus from Q
                        dqer.off() #Call to perosn specific function to do small stat work.
                    if bus.passengers.qsize() == 0:
                        #Bus to leave
                        bus.status = "Enroute"
                        bus.time_till_next_stop = distance_between(bus.route.locations[bus.location_index], bus.route.locations[(bus.location_index+1)%len(bus.route.locations)], bus.route)
                        buses_left += 1
                        temp = self.bus_q.get()        
                else:
                    #Not final, people to get on
                    if self.people != 0:
                        for i in range(0, min(int(1/Person.board_time), self.people)):
                            if bus.passengers.qsize() == bus.capacity:
                                break
                            bus.passengers.put(Person(self.name, 0))
                            self.people -= 1
                    
                    if self.people == 0 or bus.passengers.qsize() == bus.capacity:
                        #Bus to leave
                        bus.status = "Enroute"
                        bus.time_till_next_stop = distance_between(bus.route.locations[bus.location_index], bus.route.locations[(bus.location_index+1)%len(bus.route.locations)], bus.route)
                        buses_left += 1
                        temp = self.bus_q.get()
            



def distance_between(stop1, stop2, route):
    #This may be based off of calculation or database of data, effectively, return the time it takes to travel between two locations
    dist = math.sqrt(math.pow((stop1.position[0] - stop2.position[0]),2) + math.pow((stop1.position[1] - stop2.position[1]),2))
    time = math.floor(dist * Route.busy[route.busy_level])
    return time




A = BusStop("A", (0,0), 20, 1, idle_buses=1)
B = BusStop("B", (0,3), 28, 1)
C = BusStop("C", (2,5), 28, 1)
D = BusStop("D", (4, 7), 36, 2)
Stadium = BusStop("Stadium", (10,10), 0, 3)
E = BusStop("E", (8, 12), 36, 2, idle_buses=3)
F = BusStop("F", (7,10,), 80, 3)
G = BusStop("G", (5, 8), 30, 1)

route_1 = Route([A, B, C, D, Stadium], 60)
route_2 = Route((E, F, G, D, Stadium), 60)




time = 0

total_people = 0
for stop in BusStop.all_stops:
    total_people += stop.people
start_run = datetime.now()

while time <= 120:
    Route.tick_all()
    BusStop.tick_all()
    Bus.tick_all()
    time += 1
end_run = datetime.now()

print("------------")
print("Time to run: {}".format((end_run-start_run)))
print("------------")
print(Person.total_stadium, "/", total_people)
print("------------")
for (loc, arr) in Person.dict.items():
    try:
        avg = sum(arr)/len(arr)
    except:
        avg = None
    print("Avg time for passengers ({}) from {} was: {}".format(len(arr), loc, avg))
