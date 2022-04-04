# Prepare road surface
# Spatial reference system on a scale of 1 : 5,000 for data from the environmental atlas 
# from statistical blocks of the regional reference system (RBS) with sub-blocks of the city 
# and environment information system (ISU), as of December 31, 2015.

import pandas as pd
import geopandas as gpd
import os

path = os.getcwd()

surface_gdf = gpd.read_file(path + '/data/raw/road surface/shp/strassenflaechen.shp')

surface_gdf.gml_id .value_counts() # surface id
surface_gdf = surface_gdf.reset_index()  
surface_gdf.rename(columns = {'index':'surface_id'}, inplace = True)
surface_gdf = surface_gdf.to_crs(4326)
surface_gdf.rename(columns = {'FLAECHE ':'area'}, inplace = True)
surface_gdf.info()

surface_gdf.to_csv(path + "/data/output/road_surface.csv", index = False)

surface_shp = surface_gdf.to_crs(4326)
surface_shp.to_file(path + "/data/output/surface_shp.shp", index = False)

# spatial join road surface to road segment
#road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")
#road_surface = gpd.sjoin(road_shp, surface_shp, how='left', predicate = "intersects")

