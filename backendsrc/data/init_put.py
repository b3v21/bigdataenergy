import sys
import os
import csv
from pathlib import Path
import django

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

from db.models import Station, Route # noqa: E402


def parse_data(path: str, model: str) -> None:
    with open(path) as f:
        print("opened")
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            if model == "Station":
                _, created = Station.objects.get_or_create(
                    station_id=row[0],  # THIS ASSUMES THE ID IS IN THE CSV
                    name=row[1],
                    lat=row[2],
                    long=row[3],
                )
            elif model == "Route":
                stations = [Station.objects.get(station_id=int(station)) for station in row[0].strip("{").strip("}").split(", ")]
                print(stations)
                print(i)
                
                if stations == []:
                    continue
                
                route = Route.objects.create(
                    route_id = i,
                    translink_id=row[1],
                    name=row[2],
                    transport_type=row[3],
                    capacity=row[4],
                )
                route.save()
                
                for station in stations:
                    route.stations.add(station)
            # elif model == "Timetable":
            #     # import pdb; pdb.set_trace()
            #     _, created = Timetable.objects.get_or_create(
            #         station_id=Station.objects.filter(station_id=row[0])[0],
            #         route_id=Route.objects.filter(translink_id=row[1])[0],
            #         sequence=row[2],
            #         arrival_times=row[3],
            #     )
            if (i % 1000) == 0:
                print(i, "rows added!")


if __name__ == "__main__":
    PATH = (
        "./gtfsdata/routes_converted.csv"  # Change this param to read from diff file
    )
    MODEL = "Route"  # Change this param to insert other model types
    parse_data(PATH, MODEL)
