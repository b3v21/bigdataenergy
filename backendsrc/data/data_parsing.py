import pandas as pd
import csv

# THIS ONLY COLLECTS STATIONS WITHIN ZONES 1 AND 2 IN SEQ
def parse_stations():
    # get route_id, name, type from routes.txt -> insert into df
    df = None
    path = "./gtfsdata/stops.csv"
    visited_ids = []

    with open(path) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                df = pd.DataFrame(
                    columns=["station_id", "name", "lat", "long"]
                )
            else:
                if row[0] not in visited_ids and (row[6] == '1' or row[6] == '2'):
                    visited_ids.append(row[0])
                    df = df.append(
                        {
                            "station_id": row[0],
                            "name": row[2],
                            "lat": row[4],
                            "long": row[5],
                        },
                        ignore_index=True,
                    ) 
        df.to_csv("./gtfsdata/stations_converted.csv", index=False)

def parse_routes():
    # get route_id, name, type from routes.txt -> insert into df
    visited_ids = []
    
    stop_times = pd.read_csv("./gtfsdata/stop_times.csv")
    trips = pd.read_csv("./gtfsdata/trips.csv")
    routes = pd.read_csv("./gtfsdata/routes.csv")
    
    route_trip_map = {}
    trip_stop_map = {}
    
    for i, row1 in trips.iterrows():
        route_id = row1["route_id"]
        trip_id = row1['trip_id']
        if route_id in route_trip_map:
            route_trip_map[route_id].append(trip_id)
        else:
           route_trip_map[route_id] = [trip_id]
    
    for i, row2 in stop_times.iterrows():
        trip_id = row2["trip_id"]
        stop_id = row2["stop_id"]
        if trip_id in trip_stop_map:
            trip_stop_map[trip_id].append(stop_id)
        else:
            trip_stop_map[trip_id] = [stop_id]


    df = pd.DataFrame(
        columns=["stations", "translink_id", "name", "transport_type", "capacity"]
    )
    
    for i, row in routes.iterrows():
        if row["route_short_name"] not in visited_ids:
            visited_ids.append(row["route_short_name"])
            
            route_stations = set()
            
            for trip in route_trip_map[row["route_id"]]:
                for stop in trip_stop_map[trip]:
                    route_stations.add(stop)
            
            df.loc[len(df.index)] = [route_stations, row[1], row[2], row[4], 50]
            
       
    # TEMP VALUE 50
            df.to_csv("./gtfsdata/routes_converted.csv", index=False)


def parse_trips():
    # get route_id from routes.txt -> use trip_id from routes.txt to all getstop_ids,
    # stop_sequence & collect stop_time and add to list from stop_times.txt
    path1 = "./gtfsdata/routes.csv"
    path2 = "./gtfsdata/trips.csv"
    path3 = "./gtfsdata/stop_times.csv"

    translink_route_link = {}
    route_trip_link = {}
    trip_stop_link = {}
    trip_stop_times_link = {}

    visited_translink_id = set()

    routes = pd.read_csv(path1)
    trips = pd.read_csv(path2)
    stop_times = pd.read_csv(path3)

    trips_result = pd.DataFrame(
        columns=["trip_id", "route", "station", "translink_trip_id", "arrival_time","sequence"]
    )

    for index1, row1 in routes.iterrows():
        translink_id = row1["route_short_name"]
        route_id = row1["route_id"]
        
        route_trip_link[route_id] = []

        if translink_id not in visited_translink_id:
            translink_route_link[translink_id] = route_id
            visited_translink_id.add(translink_id)

    print("stage 1/4 complete")

    for index2, row2 in trips.iterrows():
        trip_id = row2["trip_id"]
        route_id = row2["route_id"]
        
        route_trip_link[route_id].append(trip_id)

    print("stage 2/4 complete")

    for index3, row3 in stop_times.iterrows():
        trip_id = row3["trip_id"]
        stop_id = row3["stop_id"]
        sequence = row3["stop_sequence"]
        arrival_time = row3["arrival_time"]
        
        if trip_id in trip_stop_link.keys():
            trip_stop_link[trip_id] += [stop_id]
        else:
            trip_stop_link[trip_id] = [stop_id]

        if (trip_id, stop_id) not in trip_stop_times_link.keys():
            trip_stop_times_link[(trip_id, stop_id)] = (sequence, arrival_time)

    print("stage 3/4 complete")
    count = 1
    for translink_id, route_id in translink_route_link.items():
        for trip_id in route_trip_link[route_id]:
            for stop_id in trip_stop_link[trip_id]:
                if (trip_id, stop_id) in trip_stop_times_link.keys():
                    seq, time = trip_stop_times_link[(trip_id, stop_id)]
                    trips_result.loc[len(trips_result.index)] = [count, translink_id, stop_id,  trip_id,  time, seq]
            count +=1
            if (count % 1000) == 0:
                print(count)
                    

    print("stage 4/4 complete")

    trips_result.to_csv("./gtfsdata/trips_converted.csv", index=False)

    print("done!")


if __name__ == "__main__":
    parse_trips()
