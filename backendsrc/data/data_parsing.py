import pandas as pd
import csv


def parse_routes():
    # get route_id, name, type from routes.txt -> insert into df
    df = None
    path = "./gtfsdata/routes.csv"
    visited_ids = []

    with open(path) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                df = pd.DataFrame(
                    columns=["translink_id", "name", "transport_type", "capacity"]
                )
            else:
                if row[1] not in visited_ids:
                    visited_ids.append(row[1])
                    df = df.append(
                        {
                            "translink_id": row[1],
                            "name": row[2],
                            "transport_type": row[4],
                            "capacity": 50,
                        },
                        ignore_index=True,
                    )  # TEMP VALUE 50
        df.to_csv("./gtfsdata/routes_converted.csv", index=False)


def parse_timetables():
    # get route_id from routes.txt -> use trip_id from routes.txt to all getstop_ids,
    # stop_sequence & collect stop_time and add to list from stop_times.txt
    path1 = "./gtfsdata/routes.csv"
    path2 = "./gtfsdata/trips.csv"
    path3 = "./gtfsdata/stop_times.csv"

    translink_route_link = {}
    route_trip_link = {}
    trip_stop_link = {}
    stop_times_link = {}

    visited_translink_id = set()
    visited_trip_stop_combo = set()

    routes = pd.read_csv(path1)
    trips = pd.read_csv(path2)
    stop_times = pd.read_csv(path3)

    result = pd.DataFrame(
        columns=["station_id", "translink_id", "sequence", "arrival_times"]
    )

    for index1, row1 in routes.iterrows():
        translink_id = row1["route_short_name"]
        route_id = row1["route_id"]

        if translink_id not in visited_translink_id:
            route_trip_link[route_id] = []
            translink_route_link[translink_id] = route_id
            visited_translink_id.add(translink_id)

    print("stage 1/4 complete")

    for index2, row2 in trips.iterrows():
        trip_id = row2["trip_id"]
        route_id = row2["route_id"]
        if route_id in route_trip_link:
            if len(route_trip_link[route_id]) < 1:
                route_trip_link[route_id] += [trip_id]

    print("stage 2/4 complete")

    for index3, row3 in stop_times.iterrows():
        trip_id = row3["trip_id"]
        stop_id = row3["stop_id"]
        sequence = row3["stop_sequence"]
        arrival_time = row3["arrival_time"]

        if (trip_id, stop_id) not in visited_trip_stop_combo:
            if trip_id not in trip_stop_link:
                trip_stop_link[trip_id] = [(stop_id, sequence)]
            else:
                trip_stop_link[trip_id] += [(stop_id, sequence)]

            if stop_id not in stop_times_link:
                stop_times_link[stop_id] = [arrival_time]
            else:
                stop_times_link[stop_id] += [arrival_time]
            visited_trip_stop_combo.add((trip_id, stop_id))

    print("stage 3/4 complete")

    for translink_id, route_id in translink_route_link.items():
        for trip_id in route_trip_link[route_id]:
            if trip_id in trip_stop_link:
                for stop_id, seq in trip_stop_link[trip_id]:
                    result = result.append(
                        {
                            "station_id": stop_id,
                            "translink_id": translink_id,
                            "sequence": seq,
                            "arrival_times": stop_times_link[stop_id],
                        },
                        ignore_index=True,
                    )

    print("stage 4/4 complete")

    result.to_csv("./gtfsdata/timetable_converted.csv", index=False)

    print("done!")


if __name__ == "__main__":
    parse_timetables()
