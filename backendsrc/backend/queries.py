from __future__ import annotations
from pathlib import Path
import django
import os
import sys
import json
from django.db.models import Q
from rest_framework.response import Response

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from db.models import Station, ItineraryCache, RouteInItinCache

ALLOWED_SUBURBS = [
    # "Toowong",
    "Indooroopilly",
    # "Taringa",
    "St Lucia",
    # "Chapel Hill",
    "West End",
    # "Bardon",
    # "Paddington",
    # "Ashgrove",
    # "Herston",
    # "Newstead",
    # "Teneriffe",
    # "New Farm",
    "Fortitude Valley",
    # "Brisbane City",
    # "Highgate Hill",
    # "South Brisbane",
    # "Kangaroo Point",
    # "East Brisbane",
    # "Dutton Park",
    # "Fairfield",
    # "Stones Corner",
    # "Coorparoo",
    # "Norman Park",
    # "Seven  Hills",
    # "Cannon Hill",
    # "Morningside",
    # "Hawthorne",
    # "Balmoral",
    # "Bulimba",
    # "Murarrie",
    # "Hamilton",
    # "Eagle Farm",
    # "Ascot",
    # "Hendra",
    # "Clayfield",
    # "Albion",
    # "Windsor",
    # "Kelvin Grove",
    # "Red Hill",
]

ALLOWED_STATIONS = ["1850", "1064", "2200", "600014"]


def get_station_suburbs() -> dict[str : list[list[str, str]]]:
    """
    This function returns a dictionary of station, suburb pairings

    """
    result = []

    stations = Station.objects.all()
    suburbs = {}

    for station in stations:
        if station.suburb in ALLOWED_SUBURBS and station.station_id in ALLOWED_STATIONS:
            if station.suburb not in suburbs:
                suburbs[station.suburb] = [
                    {
                        "id": station.station_id,
                        "name": station.name,
                        "lat": station.lat,
                        "long": station.long,
                    }
                ]
            else:
                suburbs[station.suburb].append(
                    {
                        "id": station.station_id,
                        "name": station.name,
                        "lat": station.lat,
                        "long": station.long,
                    }
                )

    for suburb, station_data in suburbs.items():
        result.append({"suburb": suburb, "stations": station_data})
    return result
