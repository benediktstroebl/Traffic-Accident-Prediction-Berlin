"""
 Prepare road surface
 
Spatial reference system on a scale of 1 : 5,000 for data from the environmental atlas 
from statistical blocks of the regional reference system (RBS) with sub-blocks of the city 
and environment information system (ISU), as of December 31, 2015.
"""
#%%
import pandas as pd
import geopandas as gpd
import os
#%%
path = os.getcwd()

def df_to_gdf(df, projection, geometry):
    crs = {'init': projection}
    gdf = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
    return gdf

#%%
surface_gdf = gpd.read_file(path + '/data/raw/road surface/shp/strassenflaechen.shp')

surface_gdf.gml_id .value_counts() # surface id
surface_gdf = surface_gdf.reset_index()  
surface_gdf.rename(columns = {'index':'surface_id',
                              'FLAECHE':'area'}, inplace = True)
surface_gdf = surface_gdf.to_crs(4326)
#%%
# surface area in square meters - almost equal to "area" variable, confirms in sqm
surface_gdf['surface_area'] = surface_gdf.to_crs(3174).area
#%%
#surface_gdf['perimeter'] = surface_gdf.to_crs(3174).length 
#surface_gdf['boundary'] = surface_gdf.boundary
#surface_gdf.set_geometry('boundary')
#surface_gdf['perimeter'] = surface_gdf.to_crs(3174).length
#surface_gdf = 
#surface_gdf.drop(['boundary'], axis=1, inplace=True)

#%%
# Nebenstraße/ side street (5882), Hauptstraße/ main road (2148)
surface_gdf.groupby(['NAM'])['surface_id'].nunique().reset_index()
#%%
# Save
surface_gdf.to_csv(path + "/data/output/road_surface.csv", index = False)
surface_gdf.to_file(path + "/data/output/surface_shp.shp", index = False)