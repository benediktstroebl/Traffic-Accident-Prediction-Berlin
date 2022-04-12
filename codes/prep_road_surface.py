"""
 Prepare road surface
 
Spatial reference system on a scale of 1 : 5,000 for data from the environmental atlas 
from statistical blocks of the regional reference system (RBS) with sub-blocks of the city 
and environment information system (ISU), as of December 31, 2015.
"""

import pandas as pd
import geopandas as gpd
import os

path = os.getcwd()

surface_gdf = gpd.read_file(path + '/data/raw/road surface/shp/strassenflaechen.shp')

surface_gdf.gml_id .value_counts() # surface id
surface_gdf = surface_gdf.reset_index()  
surface_gdf.rename(columns = {'index':'surface_id',
                              'FLAECHE':'area'}, inplace = True)
surface_gdf = surface_gdf.to_crs(4326)

# surface area in square meters - almost equal to "area" variable, confirms in sqm
surface_gdf['surface_area'] = surface_gdf.to_crs(3174).area

# Nebenstraße/ side street (5882), Hauptstraße/ main road (2148)
surface_gdf.groupby(['NAM'])['surface_id'].nunique().reset_index()

# Save
surface_gdf.to_csv(path + "/data/output/road_surface.csv", index = False)
surface_gdf.to_file(path + "/data/output/surface_shp.shp", index = False)

# Spatial join road surface to road segment
road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")
road_surface = gpd.sjoin(road_shp, surface_gdf, how='left', predicate = "intersects")
road_surface.segment_id.isna().sum() # all segments are matched

# Calculate segment width - Hauptstraße/ main road more likely to have the same width
road_length = pd.DataFrame(road_surface.groupby(['surface_id'])['length_m', 'laenge'].sum())

road_length['diff'] = road_length.laenge - road_length.length_m
road_length['diff'].hist()

road_length = road_length.reset_index().rename({'index':'index1'}, axis = 'columns')

surface_merged = road_length.merge(surface_gdf, how="left", on = "surface_id")
surface_merged['width_m'] = surface_merged.surface_area/surface_merged.length_m
# needs further tweak, surface area are polygons not just straight lines/rectangle
