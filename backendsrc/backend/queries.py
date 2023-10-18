from __future__ import annotations
from pathlib import Path
import django
import os
import sys
import json
from django.db.models import Q
from rest_framework.response import Response 
from .itins import ALLOWED_SUBURBS, ALLOWED_STATIONS

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from db.models import Station, ItineraryCache, RouteInItinCache

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
