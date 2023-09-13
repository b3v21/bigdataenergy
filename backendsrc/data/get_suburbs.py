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
reverse= RateLimiter(geolocator.reverse, min_delay_seconds=1)

def get_location(coords):
    location = reverse(coords)
    return location.raw["address"]["suburb"]

df = pd.read_csv("./stops_with_postcode_suburb.csv")
df = df[['stop_id', 'stop_lat', 'stop_lon']]
df["lat_long"] = df["stop_lat"].astype(str) + ", " + df["stop_lon"].astype(str)

df["suburb"] = df["lat_long"].apply(get_location)
df.to_csv("./output.csv", index=False)
