# Prepare detailed road network

import pandas as pd
import geopandas as gpd
import os

path = os.getcwd()

# Road network detailed
road_gdf = gpd.read_file(path + '/data/raw/road network/shp/Detailnetz-Strassenabschnitte.shp')
road_gdf.element_nr.value_counts() # segment id
road_gdf = road_gdf.reset_index()  
road_gdf.rename(columns = {'index':'segment_id'}, inplace = True)
road_gdf = road_gdf.to_crs(4326)
road_gdf.info()

road_gdf.to_csv(path + "/data/output/road_segments.csv", index = False)

road_shp = road_gdf.to_crs(4326)
road_shp.plot()

road_shp.to_file(path + "/data/output/road_shp.shp", index = False)
