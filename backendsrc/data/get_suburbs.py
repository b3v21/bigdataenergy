import ssl
import certifi
import geopy.geocoders
from geopy.geocoders import Nominatim
import csv
from geopy.exc import GeocoderTimedOut
import time
import pandas as pd
from geopy.extra.rate_limiter import RateLimiter

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

geolocator = Nominatim(user_agent="bigdataenergy", scheme="http")
reverse= RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=5)

def get_location(coords):
    location = reverse(coords)
    if location is None:
        return None
    address = location.raw.get("address")
    if address is not None:
        print(address.get("suburb"))
        return address.get("suburb")
    else: 
        print("None")
        return None

df = pd.read_csv("./gtfsdata/stops.txt")
df = df[['stop_id', 'stop_lat', 'stop_lon']]

if df["stop_lat"] is None or df["stop_lon"] is None:
    df["lat_long"] = None
    df["suburb"] = None
else:
    df["lat_long"] = df["stop_lat"].astype(str) + ", " + df["stop_lon"].astype(str)
    df["suburb"] = df["lat_long"].apply(get_location)
df.to_csv("./output.csv", index=False)
