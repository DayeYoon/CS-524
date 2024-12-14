# -*- coding: utf-8 -*-
"""CS524-T1-Create_shadow_data.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EYecJjXIv8qrksjOjcsTJUklvsC5dsmy

# Create shadow data based on building height dataset

Dataset link:


*   [Traffic Crashes](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if/about_data)
*   [Chicago Street](https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau)
*   [Chicago Boundary](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-City/ewy2-6yfk)
"""

!pip install pandas pysolar pytz
!pip install sodapy
!pip install geojson
!pip install pydeck

import pandas as pd
import requests
import altair as alt
import matplotlib.pyplot as plt
from sodapy import Socrata
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import shape
import geojson
import numpy as np

import pydeck as pdk
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon

from google.colab import drive
drive.mount('/content/gdrive')

path = "/content/gdrive/MyDrive/CS 524/CS 524 - shared folder/Project/Dataset"

client = Socrata("data.cityofchicago.org", None)
results = client.get("unjd-c2ca")
results_df = pd.DataFrame.from_records(results)

# Define the timezone for Chicago
CHICAGO_TIMEZONE = pytz.timezone('America/Chicago')

from pysolar.solar import get_altitude, get_azimuth
from datetime import datetime, timedelta
import pytz
import math
DATA_FILE = path+'/ChicagoBuildingsHeight_OpenStreetMap.csv'
OUTPUT_FILE = path+'/shadow_positions.csv'      # Output file for shadow data
DATE_TO_CALCULATE = datetime(2024, 4, 27)       # Specify the date for shadow calculation

# with open(path+'/ChicagoBuildingsHeight_OpenStreetMap.csv', 'r', encoding='utf-8') as file:
#     for _ in range(5):
#         print(file.readline())

try:
    df = pd.read_csv(DATA_FILE, sep=',', low_memory=False)
    print("Columns:", df.columns.tolist())  # Verify column names
except Exception as e:
    print(f"Error reading the data file: {e}")
    exit(1)

# Verify necessary columns exist
required_columns = ['X', 'Y', 'id', 'height', 'name']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Missing required column(s): {', '.join(missing_columns)}")
    exit(1)

# Convert 'height' to numeric and drop rows where 'height' is not available or non-numeric
df['height'] = pd.to_numeric(df['height'], errors='coerce')
df = df.dropna(subset=['X', 'Y', 'height'])

def calculate_shadow(latitude, longitude, building_height, current_time):
    # Convert local time to UTC
    local_time = CHICAGO_TIMEZONE.localize(current_time)
    utc_time = local_time.astimezone(pytz.utc)

    # Calculate sun's altitude and azimuth
    altitude = get_altitude(latitude, longitude, utc_time)
    azimuth = get_azimuth(latitude, longitude, utc_time)

    if altitude > 0:
        # Calculate shadow length in meters
        shadow_length = building_height / math.tan(math.radians(altitude))

        # Calculate shadow direction (opposite to sun's azimuth)
        shadow_direction = (azimuth + 180) % 360

        return shadow_length, shadow_direction
    else:
        # Sun is below the horizon; no shadow
        return None, None

shadow_data = []

# Iterate over each building
for index, row in df.iterrows():
    building_id = row['id']
    building_name = row.get('name', 'N/A')
    longitude = row['X']
    latitude = row['Y']
    height = row['height']  # Already converted to numeric

    # Iterate over each hour of the day
    for hour in range(24):
        current_time = DATE_TO_CALCULATE + timedelta(hours=hour)

        shadow_length, shadow_direction = calculate_shadow(latitude, longitude, height, current_time)

        # Get sun's altitude and azimuth for additional information
        sun_altitude = get_altitude(latitude, longitude, CHICAGO_TIMEZONE.localize(current_time).astimezone(pytz.utc))
        sun_azimuth = get_azimuth(latitude, longitude, CHICAGO_TIMEZONE.localize(current_time).astimezone(pytz.utc))

        shadow_data.append({
            'building_id': building_id,
            'building_name': building_name,
            'longitude': longitude,
            'latitude': latitude,
            'height_m': height,
            'datetime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'shadow_length_m': shadow_length if shadow_length is not None else 0,
            'shadow_direction_deg': shadow_direction if shadow_direction is not None else None,
            'sun_altitude_deg': sun_altitude,
            'sun_azimuth_deg': sun_azimuth
        })

    # Optional: Print progress every 100 buildings
    if (index + 1) % 100 == 0:
        print(f"Processed {index + 1} buildings...")

# Create a DataFrame from the shadow data
shadow_df = pd.DataFrame(shadow_data)

try:
    shadow_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Shadow positions have been successfully saved to {OUTPUT_FILE}")
except Exception as e:
    print(f"Error writing the output file: {e}")



import pandas as pd
import numpy as np

DATA_FILE = path+'/shadow_positions.csv'

#read DATA_FILE
df = pd.read_csv(DATA_FILE, sep=',', low_memory=False)

df.shape