import sys
import csv
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db.models import Station, Route, Timetable  # noqa: E402

def parse_data(path: str, model : str) -> None:
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if model == "Station":
                _, created = Station.objects.get_or_create(
                    station_id = row[0], # THIS ASSUMES THE ID IS IN THE CSV
                    name = row[1],
                    lat = row[2],
                    long = row[3]
                )
            elif model == "Route":
                _, created = Route.objects.get_or_create(
                    route_id = row[0],
                    station_id = row[1],
                    name = row[2],
                    transport_type = row[3],
                    capacity = row[4],
                    next_st = row[5],
                    prev_st = row[6]
                )
            elif model == "Timetable":
                _, created = Timetable.objects.get_or_create(
                    station_id = row[0],
                    route_id = row[1],
                    arrival_times = row[2]
                )
                
if __name__ == "__main__()":
    PATH = "./test.csv" # Change this param to read from diff file
    MODEL = "Station" # Change this param to insert other model types
    parse_data(PATH, MODEL)