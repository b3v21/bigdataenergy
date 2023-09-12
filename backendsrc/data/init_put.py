import sys
import os
import csv
from pathlib import Path
import django
from datetime import time
from dateutil import tz

BRIS = tz.gettz("Australia/Brisbane")


maxInt = sys.maxsize
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from db.models import *  # noqa: E402


def parse_data(path: str, model: str) -> None:
    with open(path) as f:
        print("opened")
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            if model == "Calendar":
                Calendar.objects.create(
                    service_id=row[0],
                    monday=row[1],
                    tuesday=row[2],
                    wednesday=row[3],
                    thursday=row[4],
                    friday=row[5],
                    saturday=row[6],
                    sunday=row[7],
                )
            if model == "Station":
                Station.objects.create(
                    station_id=row[0],  # THIS ASSUMES THE ID IS IN THE CSV
                    station_code=row[1],
                    name=row[2],
                    lat=row[4],
                    long=row[5],
                    location_type=row[8],
                )
            elif model == "Route":
                Route.objects.create(
                    route_id=row[0],
                    name=row[1],
                    transport_type=row[4],
                    capacity=50,
                )
            elif model == "Shape":
                Shape.objects.create(
                    shape_id=row[0],
                    shape_pt_lat=row[1],
                    shape_pt_lon=row[2],
                    shape_pt_sequence=row[3],
                )
            elif model == "Timetable":
                # import pdb; pdb.set_trace()
                time_format = row[1].strip("'").split(":")
                if int(time_format[0]) >= 24:
                    time_object = time(
                        int(time_format[0]) - 24, int(time_format[1]), tzinfo=BRIS
                    )
                else:
                    time_object = time(
                        int(time_format[0]), int(time_format[1]), tzinfo=BRIS
                    )
                Timetable.objects.create(
                    trip_id=Trip.objects.filter(trip_id=row[0]).first(),
                    station=Station.objects.filter(station_id=row[3]).first(),
                    arrival_time=time_object,
                    sequence=row[4],
                )
            elif model == "Trip":
                Trip.objects.get_or_create(
                    trip_id=row[2],
                    route_id=Route.objects.filter(route_id=row[0]).first(),
                    service_id=Calendar.objects.filter(service_id=row[1]).first(),
                    shape_id=Shape.objects.filter(shape_id=row[6]).first(),
                )
            if (i % 1000) == 0:
                print(i, "rows added!")


if __name__ == "__main__":
    # Timetable.objects.all().delete()
    PATH = "./gtfsdata/stop_times.txt"  # Change this param to read from diff file
    MODEL = "Timetable"  # Change this param to insert other model types
    parse_data(PATH, MODEL)
