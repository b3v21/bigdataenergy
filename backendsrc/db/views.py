from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from db.models import Station, SimulationOutput
from rest_framework.response import Response
from db.serializers import SimulationOutputSerializer
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from backend.sim import run_simulation, generate_itins
from backend.queries import get_station_suburbs
from logging import warning
from backend.sim import INPUT_ITINS


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
        output = generate_itins(request.data)

    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(data=output, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def list_saved_sims(request: Request) -> Response:
    """
    Reponisble for returning the list of saved simulations to the frontend.
    NOTE: This will send just sim ids for now
    """

    print(f"Request for list of saved simulations received.")

    output = [{"sim_id": 1}, {"sim_id": 2}, {"sim_id": 3}]

    return Response(data=output, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_sim_data(request: Request) -> Response:
    """
    Given a sim_id, this will return the data for that sim in the same
    format as the sim_request response.

    request o.t.f:
    {
        sim_id: int
    }
    """

    if not request.data:
        warning(f"No user data received.")

    print(f"Request for saved sim received")

    try:
        if request.data["sim_id"] == 1:
            user_data = {
                "env_start": 0,
                "time_horizon": 355,
                "itineraries": [INPUT_ITINS["1850"][0]],
                "snapshot_date": "2023-07-12",
                "active_suburbs": "St Lucia",
                "active_stations": "1850",
            }

            output = run_simulation(user_data, 1)

    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(data=output, status=status.HTTP_201_CREATED)
