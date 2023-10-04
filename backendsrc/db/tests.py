from django.test import TestCase
import requests

# from models import Station
from datetime import time, date, datetime
import json
import ast

# from ..backend.sim import Station, Itinerary

# Create your tests here.

api = "https://api.tripgo.com/v1/routing.json"
key = "2286d1ca160dd724a3da27802c7aba91"
# modes = ["pt_pub_bus", "pt_pub_train"]
modes = ["pt_pub_bus"]
# endStation = "(-27.464867,153.009186)" #default suncorp stadium

endStation = "(-27.4979739, 153.0111389)\"UQ Chancellor's Place, zone D"


# save itinerary to database
# to do: update new itineraries to database
def cacheItinerary():
    return False


"""
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
        
    """


def does_contain(itin, itins):
    for i in itins:
        if i["routes"] == itin["routes"]:
            return True
    return False


"""
response -> all raw response data from api call
num_itins -> num of itins that are generated for each group, which is the different combinatinos of travel methods
start_station_id -> station_id (ie '001815') for the station that was specified as the start location for api call
start_itin_id -> the int val to start the id's from

Returns -> array of properly formatted itins
"""


def formatItins(response, num_itins, start_station_id, start_itin_id):
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
    print(itins)


# call the api for itinerary of a single trip
# to do: json data manipulation
# to do: decide on parameters
def callTripGoAPI(api, parameters, headers):
    response = requests.get(api, params=parameters, headers=headers)
    if response.status_code == 200:
        print("sucessfully fetched TripGo data")
        # print(response.json())
        # print()
        # print(response.json().get("groups", {})[0].get("trips"))
        return response.json()
    else:
        raise Exception(f"{response.status_code}")


"""
#get the formatted position of a station
def getStationPos(station: Station):
    pos = station.pos
    return(f"{pos[0]}, {pos[1]}")
"""

if __name__ == "__main__":
    parameters = {
        "v": "11",
        "from": '(-27.501517,153.006885)"Boomerang Rd W at St Lucia South near Hawken Dr"',
        "to": endStation,
        "modes": modes,
        "bestOnly": "true",
        "includeStops": "false",
        "bestOnly": "true",
    }
    headers = {"X-TripGo-Key": key}

    response = callTripGoAPI(api, parameters, headers)
    formatItins(response, 3, "001815", 0)
