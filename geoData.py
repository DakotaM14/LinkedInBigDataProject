import geopandas as gpd
import os
import pandas as pd
import matplotlib.pyplot as plt

# Directory where your state directories are stored
states_directory = "geojson-us-city-boundaries-master/cities"

# Initialize an empty GeoDataFrame
all_cities_gdf = gpd.GeoDataFrame()

# Iterate through each state directory
for state_abbrev in os.listdir(states_directory):
    state_path = os.path.join(states_directory, state_abbrev)
    
    # Check if it's a directory
    if os.path.isdir(state_path):
        # Iterate through each file in the state directory
        for filename in os.listdir(state_path):
            if filename.endswith(".json"):
                file_path = os.path.join(state_path, filename)
                
                # Read the JSON file into a GeoDataFrame
                city_gdf = gpd.read_file(file_path)
                
                # Concatenate the individual GeoDataFrame to the overall GeoDataFrame
                all_cities_gdf = gpd.GeoDataFrame(pd.concat([all_cities_gdf, city_gdf], ignore_index=True))

