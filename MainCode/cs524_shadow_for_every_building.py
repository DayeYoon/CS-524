#!/usr/bin/env python
# coding: utf-8

# https://pybdshadow.readthedocs.io/en/latest/example/example.html

# In[6]:


import pandas as pd
import geopandas as gpd
import pybdshadow
import fiona


# In[7]:


#Read building data
buildings = gpd.read_file(r'C:\Users\DAYE\Downloads\ChicagoBuildingsHeight_OpenStreetMap.geojson')
buildings.head(5)


# In[4]:


buildings.to_csv('ChicagoBuildingsHeight_OpenStreetMap.csv', index=False)


# In[5]:


buildings.shape


# In[6]:


# Define a list of columns to keep
columns_to_keep = ['id', 'addr:street', 'addr:street:prefix', 'addr:street:name',
                   'addr:street:type', 'height', 'geometry', 'building:levels']

# Keep only specific columns and drop the rest
buildings = buildings[columns_to_keep]

buildings.rename(columns={'building:levels': 'Floor'}, inplace=True)

buildings.head(5)


# In[7]:


buildings.shape


# In[8]:


# CRS setting (Set the appropriate EPSG code as needed to match the data.)
buildings = buildings.to_crs("EPSG:4326")  # set to WGS 84


# ## Avenue->AVE, West->W

# In[9]:


column_names = ['addr:street:prefix', 'addr:street:type']

for column in column_names:
  unique_values = buildings[column].unique()
  print(f"Unique values in column '{column}' : {unique_values}")


# In[10]:


replace_str = {
    #ddr:street:prefix
    'West': 'W',
    'East': 'E',
    'North': 'N',
    'South': 'S',
    
    #addr:street:type
    'Street': 'ST',
    'Plaza': 'PLZ',
    'Boulevard': 'BLVD',
    'Avenue': 'AVE',
    'Drive': 'DR',
    'Place': 'PL',
    'Court': 'CT',
    'CT': 'CT',
    'Road': 'RD'
}

buildings.replace(replace_str, regex=False, inplace=True)
buildings.head()


# In[11]:


buildings.shape


# In[12]:


#buildings.to_csv('modified_ChicagoBuildingsHeight.csv', index=False)
buildings.to_file("modified_ChicagoBuildingsHeight.geojson", driver="GeoJSON")


# In[13]:


buildings.to_csv('modified_ChicagoBuildingsHeight.csv', index=False)


# ## Resolve below problem
# ![image.png](attachment:fb73a522-1ad3-4467-98ca-925e691bc970.png)

# In[ ]:


buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight.geojson')

# Dictionary for replacements
replace_str = {
    # addr:street:prefix
    'West': 'W',
    'East': 'E',
    'North': 'N',
    'South': 'S',
    
    # addr:street:type
    'Street': 'ST',
    'Plaza': 'PLZ',
    'Boulevard': 'BLVD',
    'Avenue': 'AVE',
    'Drive': 'DR',
    'Place': 'PL',
    'Court': 'CT',
    'Road': 'RD'
}

# Function to split and replace addr:street into prefix, name, and type
def split_and_replace(addr_street):
    # Handle None values
    if pd.isna(addr_street):
        return '', '', ''
    
    parts = addr_street.split()
    prefix, name, street_type = '', '', ''

    # Check if the first part is a direction (prefix)
    if parts[0] in replace_str:
        prefix = replace_str[parts[0]]
        parts = parts[1:]  # Remove the prefix from parts

    # Check if the last part is a street type
    if parts[-1] in replace_str:
        street_type = replace_str[parts[-1]]
        parts = parts[:-1]  # Remove the type from parts

    # Join the remaining parts as the street name
    name = ' '.join(parts).upper()

    return prefix, name, street_type

# Apply the function and update the columns
buildings[['addr:street:prefix', 'addr:street:name', 'addr:street:type']] = buildings['addr:street'].apply(lambda x: pd.Series(split_and_replace(x)))

# Save the updated GeoDataFrame to a new file
buildings.to_file("modified_ChicagoBuildingsHeight_filled.geojson", driver="GeoJSON")
buildings.to_csv('modified_ChicagoBuildingsHeight_filled.csv', index=False)


# # Result
# ![image.png](attachment:61a2fe97-8fb0-48e8-8e02-cc946316c5ec.png)

# ## Adding the building_id for pybdshadow

# In[8]:


#Read building data
buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight_filled.geojson')
buildings.head(5)


# In[9]:


# CRS setting (Set the appropriate EPSG code as needed to match the data.)
buildings = buildings.to_crs("EPSG:4326")  # set to WGS 84


# In[10]:


buildings = pybdshadow.bd_preprocess(buildings)
buildings


# In[18]:


#save geojason
buildings.to_file('modified_ChicagoBuildingsHeight_buildingid.geojson', driver='GeoJSON')


# In[19]:


buildings.to_csv('modified_ChicagoBuildingsHeight_buildingid.csv', index=False)


# ## adding the STREETNAME to modified_ChicagoBuildingsHeight_buildingid.geojason

# In[20]:


transportation = gpd.read_file(r'C:\Users\DAYE\transportation_20241106(2).geojson')
transportation.head()


# In[16]:


transportation = pd.read_csv(r'C:\Users\DAYE\Chicago_Streets_with_street_segment_id.csv')
transportation.head()


# In[17]:


# Define a list of columns to keep
keep_column = ['the_geom', 'PRE_DIR', 'STREET_NAM', 'STREET_TYP', 'STREETNAME', 'street_segment_id']

# Keep only specific columns and drop the rest
transportation = transportation[keep_column]

transportation.head(5)


# In[18]:


modified_buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight_buildingid.geojson')
modified_buildings.head()


# # Building's centroid

# In[18]:


import geopandas as gpd

# Buildings data load
buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight_buildingid.geojson')

# Convert to the projected coordinate system
projected_crs = "EPSG:26916"  # UTM Zone 16N
buildings = buildings.to_crs(projected_crs)

# calculate the centroid
buildings["centroid"] = buildings.geometry.centroid

# save
buildings_centroids = buildings.set_geometry("centroid")
buildings_centroids = buildings_centroids.drop(columns="geometry")
buildings_centroids.to_file("buildings_centroids.geojson", driver="GeoJSON")


# In[50]:


from shapely.geometry import Point, LineString
from shapely import wkt
import geopandas as gpd
import pandas as pd

# Load the buildings centroids GeoJSON file
buildings_centroids = gpd.read_file(r'C:\Users\DAYE\buildings_centroids.geojson')
# Load the Chicago streets CSV file
streets = pd.read_csv(r'C:\Users\DAYE\Chicago_Streets_with_street_segment_id.csv')

# Convert the geometry column in streets to shapely objects and GeoDataFrame
streets["geometry"] = streets["geometry"].apply(wkt.loads)
streets = gpd.GeoDataFrame(streets, geometry="geometry", crs="EPSG:4326")

# Convert to projected CRS (UTM Zone 16N)
buildings_centroids = buildings_centroids.to_crs("EPSG:26916")
streets = streets.to_crs("EPSG:26916")

# Explode MultiLineString into individual LineStrings
streets = streets.explode(index_parts=False)

# Define a function to assign the closest segment
def find_closest_segment(building, street_data, max_distance=50):
    closest_segment = None
    min_distance = float("inf")
    for _, row in street_data.iterrows():
        distance = row["geometry"].distance(building.geometry)
        if distance < max_distance:
            if distance < min_distance:
                min_distance = distance
                closest_segment = row["street_segment_id"]
    return closest_segment

# Step 1: Assign street_segment_id1 (closest segment)
buildings_centroids["street_segment_id1"] = buildings_centroids.apply(
    lambda building: find_closest_segment(building, streets, max_distance=50), axis=1
)

# Step 2: Assign street_segment_id2 (second closest segment)
def find_second_closest_segment(building, street_data, exclude_segment, max_distance=50):
    second_closest = None
    min_distance = float("inf")
    for _, row in street_data.iterrows():
        if row["street_segment_id"] == exclude_segment:
            continue
        distance = row["geometry"].distance(building.geometry)
        if distance < max_distance:
            if distance < min_distance:
                min_distance = distance
                second_closest = row["street_segment_id"]
    return second_closest

buildings_centroids["street_segment_id2"] = buildings_centroids.apply(
    lambda building: find_second_closest_segment(
        building, streets, building["street_segment_id1"], max_distance=50
    ),
    axis=1,
)

# Save results to GeoJSON
buildings_centroids.to_file(r'C:\Users\DAYE\buildings_with_two_segments_fixed.geojson', driver="GeoJSON")

# Show the first few rows of the resulting data
buildings_centroids[["id", "street_segment_id1", "street_segment_id2"]].head()


# In[51]:


buildings_centroids.to_file("buildings_with_segments2.geojson", driver="GeoJSON")
buildings_centroids.to_csv('buildings_with_segments2.csv', index=False)


# In[29]:


buildings_centroids.head(10)


# In[49]:


from shapely.geometry import Point, LineString
from shapely import wkt
import geopandas as gpd
import pandas as pd

# Load the buildings centroids GeoJSON file
buildings_centroids = gpd.read_file(r'C:\Users\DAYE\buildings_centroids.geojson')
# Load the Chicago streets CSV file
streets = pd.read_csv(r'C:\Users\DAYE\Chicago_Streets_with_street_segment_id.csv')

# Convert geometry column and CRS
streets["geometry"] = streets["geometry"].apply(wkt.loads)
streets = gpd.GeoDataFrame(streets, geometry="geometry", crs="EPSG:4326")
buildings_centroids = buildings_centroids.to_crs("EPSG:26916")
streets = streets.to_crs("EPSG:26916")

# Explode MultiLineString into individual LineStrings
streets = streets.explode(index_parts=False)
street_sindex = streets.sindex  # Build spatial index for streets

# Define function to find the closest segment
def find_closest_segments(building, max_distance=50):
    possible_matches_index = list(street_sindex.intersection(building.bounds))
    possible_matches = streets.iloc[possible_matches_index]
    segments = []
    for _, row in possible_matches.iterrows():
        distance = row["geometry"].distance(building)
        if distance < max_distance:  # Check within max_distance
            segments.append((row["street_segment_id"], distance))
    return sorted(segments, key=lambda x: x[1])  # Sort by distance

# Assign the single closest segment to each building
def assign_single_segment(building):
    segments = find_closest_segments(building, max_distance=50)
    if len(segments) > 0:
        return segments[0][0]  # Closest segment
    return None

# Apply the function to assign single closest segment
buildings_centroids["street_segment_id1"] = buildings_centroids.geometry.apply(
    lambda building: assign_single_segment(building)
)

# Save results to a new GeoJSON file
#buildings_centroids.to_file("/mnt/data/buildings_with_single_segment.geojson", driver="GeoJSON")

# Display the first few rows of the updated data
buildings_centroids[["id", "street_segment_id1"]].head()


# In[20]:


# Convert street names to uppercase for consistent matching
#transportation['street_nam'] = transportation['street_nam'].str.upper()
#modified_buildings['addr:street:name'] = modified_buildings['addr:street:name'].str.upper()

# Create a dictionary mapping of (pre_dir, street_nam) to streetname in transportation
streetname_map = transportation.set_index(['PRE_DIR', 'STREET_NAM'])['street_segment_id'].to_dict()

# Define a function to map streetname based on pre_dir and addr:street:name
def add_streetname(row):
    key = (row['addr:street:prefix'], row['addr:street:name'])
    return streetname_map.get(key, None)  # Return the mapped streetname or None if no match

# Apply the function to add the streetname column in modified_buildings
modified_buildings['street_segment_id'] = modified_buildings.apply(add_streetname, axis=1)

# Save the updated GeoDataFrame to a new file
modified_buildings.to_file("modified_ChicagoBuildingsHeight_streetname2.geojson", driver="GeoJSON")


# In[21]:


modified_buildings.to_csv('modified_ChicagoBuildingsHeight_streetname2.csv', index=False)


# In[22]:


modified_buildings.head()


# ## 👆🏻 modified_ChicagoBuildingsHeight_streetname.geojson -> Chicago building height with streetname of Road dataset

# # 2. shadow calculation

# In[67]:


import pandas as pd
import geopandas as gpd
import pybdshadow
import fiona

buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight_buildingid.geojson')


# In[68]:


# Remove 'm' and convert to a numeric value
buildings['height'] = buildings['height'].str.replace('m', '', regex=False)
buildings['height'] = pd.to_numeric(buildings['height'], errors='coerce')


# In[69]:


# Given UTC time
date = pd.to_datetime('2023-02-04 17:00:00')\
    .tz_localize('America/Chicago')\
    .tz_convert('UTC')

# Calculate shadows
shadows = pybdshadow.bdshadow_sunlight(buildings, date, roof=True, include_building=False)
shadows


# In[36]:


#remove POLYGON EMPTY
shadows = shadows[~shadows['geometry'].is_empty]

shadows


# In[28]:


shadows.to_csv('shadows_Spring_Sunset.csv', index=False)


# In[29]:


modified_buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight_streetname2.geojson')
modified_buildings.head(5)


# ## Adding the id and streetname in the shadows dataset

# In[70]:


shadows = shadows
modified_buildings = gpd.read_file(r'C:\Users\DAYE\modified_ChicagoBuildingsHeight_streetname2.geojson')


# Select relevant columns from modified_buildings for merging
columns_to_merge = [
    "id",
    "building_id",
    "street_segment_id",
    "addr:street", 
    "addr:street:prefix", 
    "addr:street:name", 
    "addr:street:type"
]
modified_buildings_subset = modified_buildings[columns_to_merge]

# Merge shadows and modified_buildings on building_id
shadows_merged = shadows.merge(modified_buildings_subset, on="building_id", how="left")

# Save the result to a new GeoJSON file
shadows_merged.to_file("shadows_street_info_Winter_Sunset2.geojson", driver="GeoJSON")

# Display the first few rows to confirm
#print(shadows_merged.head())


# In[38]:


shadows_merged.shape


# In[71]:


shadows_merged.to_csv('shadows_street_info_Winter_Sunset2.csv', index=False)


# # ⭐Datasets⭐
# * modified_ChicagoBuildingsHeight.csv: change the Avenue->AVE, West->W ....
# * modified_ChicagoBuildingsHeight_filled.csv : fill the blank of the street name, direction and street type
# * modified_ChicagoBuildingsHeight_buildingid.csv: Chicagobuildingheight(original data) + building_id
# * modified_ChicagoBuildingsHeight_streetname.csv: Chicagobuildingheight(original data) + building_id + streetname(1782, 1235,...) of Road dataset
# * shadows.csv: Result of shadow calculation
# * shadows_street_info.csv: 1PM shadow geometry + building_id + streetname

# # Visualization 3D map with shadow data

# In[60]:


import pydeck as pdk
import geopandas as gpd

# Set the base coordinates (centered on Chicago)
view_state = pdk.ViewState(
    latitude=41.8781,  # Latitude of Chicago
    longitude=-87.6298,  # Longitude of Chicago
    zoom=12,
    pitch=45,
)

# Configure the 3D building layer
building_layer = pdk.Layer(
    "PolygonLayer",
    data=buildings,
    get_polygon="geometry.coordinates",  # Extract polygon coordinates from geometry
    get_elevation="height",  # Set elevation based on the 'height' column
    elevation_scale=1,
    extruded=True,
    get_fill_color="[255, 165, 0, 150]",  # Display in semi-transparent orange
    get_line_color=[255, 255, 255],  # Border color
    pickable=True,
    auto_highlight=True,
)

# Configure the shadow layer (2D)
shadow_layer = pdk.Layer(
    "GeoJsonLayer",
    data=shadows.__geo_interface__,  # Convert GeoDataFrame to GeoJson format
    opacity=0.5,
    get_fill_color=[0, 0, 0, 100],  # Semi-transparent gray
    get_line_color=[255, 255, 255],  # White border
    stroked=False,  # No border outline
)

# Create the pydeck Deck
deck = pdk.Deck(
    layers=[building_layer, shadow_layer],
    initial_view_state=view_state,
    map_style="light",
)

# Output as HTML
deck.to_html("chicago_3d_buildings_with_shadows.html")

