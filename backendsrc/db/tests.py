from django.test import TestCase
import requests
#from models import Station
from datetime import time, date, datetime
import json
import ast
#from ..backend.sim import Station, Itinerary

# Create your tests here.

api = "https://api.tripgo.com/v1/routing.json"
key = "2286d1ca160dd724a3da27802c7aba91"
#modes = ["pt_pub_bus", "pt_pub_train"]
modes = ["pt_pub_bus"]
endStation = "(-27.464867,153.009186)" #default suncorp stadium 



#save itinerary to database
#to do: update new itineraries to database
def cacheItinerary():
    return False 
'''
def createItineraries(stations: list[Station]):
    #get cached initeraries where the start station is in the list
    #to do: create database structure
    db_itin = ItineraryM.objects.all().filter(start_id__in=list(map(lambda station: station.id, stations)))
    sim_itineraries = []

    for station in stations: 
        cached = db_itin.filter(start_id=station.id)
        newItin = None
        if cached:
              #todo: create Itinerary object
              newItin = Itinerary()
        else:
            stationPos = getStationPos(station)
            parameters = {
                "v": "11",
                "from" : stationPos,
                "to" : endStation,
                "modes": modes,
                "bestOnly": "true",
                "includeStops": "false"
            }
            headers = {
                "X-TripGo-Key": key  
            }
            data = callTripGoAPI(api, parameters, headers)
            #todo: create Itinerary object
            newItin = cacheItinerary(data)
        sim_itineraries.append(newItin)

    return sim_itineraries
        
    '''

#call the api for itinerary of a single trip
#to do: json data manipulation
#to do: decide on parameters
def callTripGoAPI(api, parameters, headers):
        response = requests.get(api, params = parameters, headers = headers)
        if response.status_code == 200:
            print("sucessfully fetched TripGo data")
            print(response.json().get("groups", {})[0].get("trips"))
            return response.json()
        else:
            raise Exception(f"{response.status_code}")

'''
#get the formatted position of a station
def getStationPos(station: Station):
    pos = station.pos
    return(f"{pos[0]}, {pos[1]}")
'''

if __name__ == "__main__":
    parameters = {
                "v": "11",
                "from" : "(-27.335962, 152.952169)",
                "to" : endStation,
                "modes": modes,
                "bestOnly": "true",
                "includeStops": "false"
            }
    headers = {
                "X-TripGo-Key": key  
            }

    callTripGoAPI(api, parameters, headers)

