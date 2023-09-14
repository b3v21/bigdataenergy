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
reverse= RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=3, error_wait_seconds=10, swallow_exceptions=True)

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

def get_suburbs():
    df = pd.read_csv("./stops_with_postcode_suburb.csv")
    df = df[['stop_id', 'stop_lat', 'stop_lon']]
    df["lat_long"] = df["stop_lat"].astype(str) + ", " + df["stop_lon"].astype(str)

    df["suburb"] = df["lat_long"].apply(get_location)
    df.to_csv("./output.csv", index=False)

def estimate_suburbs():
    df = pd.read_csv("./output.csv")
    
    for i,row in df.iterrows():
        if i == 0:
            df.at[i,'suburb_est'] = df.at[i,'suburb'] 
        if pd.isna(df.at[i,'suburb']):
            df.at[i,'suburb_est'] = df.at[i-1,'suburb_est']
        else:
            df.at[i,'suburb_est'] = df.at[i, 'suburb']
        if i % 100 == 0:
            print(i)
    df.to_csv("./output2.csv", index=False)

estimate_suburbs()