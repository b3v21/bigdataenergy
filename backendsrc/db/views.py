from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from db.models import Station, SimulationOutput
from rest_framework.response import Response
from db.serializers import StationSerializer
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from backend.sim import run_simulation, generate_itins
from backend.queries import get_station_suburbs, get_cached_itineraries
from logging import warning


@api_view(["POST"])
def sim_request(request: Request, sim_id: int) -> Response:
    """
    This is the request responsible for sending user data from the
    frontend -> sim, then running the sim, then sending the sim data from
    the backend -> frontend, and also uploading to the database.

    request.data is currently expected to be a dict containing the following fields:
    {
        "env_start": int,
        "time_horizon": int,
        "itineraries":
        [
            {
                "itinerary_id" : 0,
                "routes" : [
                    {
                        "route_id": "412-3136",
                        "start": "0",
                        "end": "1850"
                    }
                ]
            }
        ]
        "snapshot_date": str, (yyyy-mm-dd format)
        "active_suburbs": list[str], (suburb names)
        "active_stations": list[str], (station ids)
    }

    NOTE: Go to test_sim.py to see examples
    """

    print(f"Simulation #{sim_id} request recieved.")
    if not request.data:
        warning(f"Simulation #{sim_id} has not recieved any user data.")

    print(f"Running simulation #{sim_id}.")
    output = run_simulation(request.data, sim_id)

    return Response(data=output, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def station_suburbs(request: Request) -> Response:
    """
    This is the request responsible for returning the station, suburb pairings
    to be presented to the user in the frontend.

    Currently has no body but perhaps later on a frontend setting could edit this

    return json of the form:
    [
        {
            "suburb" : suburb_name,
            "stations" : [
                {
                    "id" : 0,
                    "name" : "station"
                    "lat" : 0.0,
                    "long" : 0.0,
                }, ...
            ]
        }, ...
    ]
    """

    print(f"Sending location data to backend")

    output = get_station_suburbs()

    return Response(data=output, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def itin_check(request: Request) -> Response:
    """
    this is the request responsible for receiving the active stations and generating corresponding itineraries.
       request.data is currently expected to be a dict containing the following fields:
    {
        "env_start": int,
        "time_horizon": int,
        "snapshot_date": str, (yyyy-mm-dd format)
        "active_stations": [
                 {
                    "station_id" : str,
                    "lat":float,
                    "long":float
                }
            ]
    }

    return json of the form:
    "itineraries":
            [
                {
                    "itinerary_id" : 0,
                    "routes" : [
                        {
                            "route_id": "412-3136",
                            "start": "0",
                            "end": "1850"
                        }
                    ]
                }
            ]

    """
    if not request.data:
        warning(f"No user data received.")

    print(f"Request for itineraries received")
    try:
        output = {"itinieraries": generate_itins(request.data)}
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    print(output)

    return Response(data=output, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def cached_itineraries(request: Request) -> Response:
    """
    This is the request responsible for returning the cached itineraries
    to be presented to the user in the frontend.

    request.data is currently expected to be of the following form:
    [
        {
            "start" : "station_id",
            "end" : "station_id",
        }, ...
    ]

    return json of the form:
    [
        {
            "itinerary_id" : 0,
            "routes" : [
                {
                    "route_id": "412-3136",
                    "start": "0",
                    "end": "1850"
                }
            ]
        }
    ]
    """
    if not request.data:
        warning(
            "No station data was given to check cached itineraries, see views.py for correct request format"
        )

    print(f"Collecting cached itineraries from backend")

    output = get_cached_itineraries(request.data)

    return Response(data=output, status=status.HTTP_201_CREATED)


######################## PRACTICE VIEWS ########################
@api_view(["GET", "POST"])
def station_list(request):
    if request.method == "GET":
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = StationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def station_details(request, pk):
    try:
        stations = Station.objects.get(pk=pk)
    except Station.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = StationSerializer(stations)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = StationSerializer(stations, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        stations.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
