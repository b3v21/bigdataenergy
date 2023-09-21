from __future__ import annotations
from pathlib import Path
import django
import os
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from db.models import Station


def get_station_suburbs() -> dict[str: list[list[str, str]]]:
    """
    This function returns a dictionary of station, suburb pairings
    
    """
    result = []
    
    stations = Station.objects.all()
    suburbs = {}
    
    for station in stations:
        if station.suburb not in suburbs:
            suburbs[station.suburb] = [{"id" : station.station_id, "name" : station.name}]
        else:
            suburbs[station.suburb].append({"id" : station.station_id, "name" : station.name})
            
    for suburb, station_data in suburbs.items():
        result.append({"suburb" : suburb, "stations" : station_data})
    
    return result
    
