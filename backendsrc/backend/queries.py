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

from db.models import Station, ItineraryCache, RouteInItinerary


def get_station_suburbs() -> dict[str : list[list[str, str]]]:
    """
    This function returns a dictionary of station, suburb pairings

    """
    result = []

    stations = Station.objects.all()
    suburbs = {}

    for station in stations:
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


def get_cached_itineraries(request_data: list[dict[str, str]]) -> Response:
    """
    This function returns a list of cached itineraries
    """
    result = []
    start_stations = []

    for request in request_data:
        start_stations.append(request["start"])

    start_routes = RouteInItinerary.objects.filter(start__in=start_stations)
    cached_itins = ItineraryCache.objects.filter(
        Q(routes__in=start_routes) & Q(sequence=0)
    )

    for itin in cached_itins:
        itin_routes_result = ItineraryCache.objects.filter(
            itinerary_id=itin.itinerary_id
        ).order_by("sequence")

        itin_routes = []
        for route in itin_routes_result:
            itin_routes.append(
                {
                    "route_id": route.route_id,
                    "start": route.start,
                    "end": route.end,
                }
            )

        result.append(
            {
                "itinerary_id": itin.itinerary_id,
                "routes": itin_routes,
            }
        )

    return result
