"""
Prepare detailed road network

Road sections as part of the detailed road network of Berlin for traffic purposes, 
contains other roads and paths in addition to the classified road network.
"""
#%%
import pandas as pd
import geopandas as gpd
import os
import shapely
import numpy as np
#import pygeos

#%%
path = os.getcwd()

#%%
# Road network detailed
road_gdf = gpd.read_file(path + '/data/raw/road network/shp/Detailnetz-Strassenabschnitte.shp')
road_gdf.element_nr.value_counts() # element_nr unique segment id
road_gdf = road_gdf.reset_index()  # create new segment id
road_gdf.rename(columns = {'index':'segment_id'}, inplace = True)

road_gdf = road_gdf.to_crs(4326)
#%%
# segment length in meters - almost equal to "laenge" variable, confirms in meters
road_gdf['length_m'] = road_gdf.to_crs(3174).length 
road_shp = road_gdf.to_crs(4326)
# save road_shp with linestrings as geometry
road_shp.to_file(path + "/data/output/road_shp.shp", index = False)

#%% tag if main street  or side street
surface_gdf = gpd.read_file(path + '/data/output/surface_shp.shp')
#road_shp = gpd.read_file(path + "/data/output/road_shp.shp")

#road_surface = gpd.sjoin(surface_gdf, road_shp,  how='left', predicate = "intersects")
#road_surface.segment_id.isna().sum() 

# 153 side street, 9 main street
#road_surface[road_surface.segment_id.isna()].groupby(['NAM'])['surface_id'].nunique() 
#surface_gdf.groupby(['NAM'])['surface_id'].nunique().reset_index() 

# for unmatched assign 5% probability of being main street
road_surface = gpd.sjoin(road_shp, surface_gdf,  how='left', predicate = "intersects").drop_duplicates(subset = "segment_id", keep = "first")
road_surface.surface_id.isna().sum()  #2785 unmatched

street_append = road_surface[road_surface.surface_id.isna()][["segment_id"]]
street_append = street_append.reset_index(drop=True)

street_append.segment_id.isna().sum()

import random
random.seed(28)
x=random.choices([0,1], weights = [153, 9], k = 2785)
street_type = pd.DataFrame(x, columns = ['side_street'])
#street_type = street_type.reset_index()  

street_assign = pd.concat([street_append, street_type], axis=1, ignore_index=True)
street_assign = street_assign.rename(columns={street_assign.columns[0]: 'segment_id',
                                              street_assign.columns[1]: 'side_street'})

surface_gdf.groupby(['NAM'])['surface_id'].nunique().reset_index()

road_surface['side_street'] = np.where(road_surface['NAM'] == "Nebenstraße", 1,0)

road_type = road_surface.merge(street_assign, how = "left", on = "segment_id")
road_type['side_strt'] =road_type['side_street_x'].fillna(0) + road_type['side_street_y'].fillna(0)
road_type = road_type[['segment_id', 'surface_ar', 'side_strt']]


#%%
# return the midpoint of a segment
road_gdf['midpoint'] = road_gdf.centroid 

road_gdf['mid_lat'] = road_gdf.centroid.x

road_gdf['mid_lon'] = road_gdf.centroid.y

road_gdf_merged = road_gdf.merge(road_type, how = "left", on = "segment_id")

#%%
# Save csv with midpoint, road length, street type
#road_gdf_merged.to_csv(path + "/data/output/road_segments.csv", index = False) # with the midpoint in csv format

road_gdf_merged.to_csv(path + "/data/processed/road_segments.csv", index = False) # with the midpoint in csv format

#%%
# Save road_shp with road length, surface area, street type
road_segments_shp2 = road_shp.merge(road_type[["segment_id", "surface_ar", "side_strt"]], how = "left", on = "segment_id") # without midpoint in .shp format
road_segments_shp = road_segments_shp2.merge(road_gdf[["segment_id", "mid_lat", "mid_lon"]], how = "left", on = "segment_id") # without midpoint in .shp format

road_segments_shp.to_file(path + "/data/output/road_segments_shp.shp", index = False) # with linestrings as geometry

#%%

###############################
# Check midpoints - correct
#def df_to_gdf(df, projection, geometry):
#    crs = {'init': projection}
#    gdf = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
#    return gdf

#c = road_gdf[road_gdf['segment_id'] == 30000] 

#c_p = df_to_gdf(c[['segment_id', 'midpoint']], 'epsg:4326', c.midpoint).to_crs(3174)
#c_r = df_to_gdf(c[['segment_id', 'geometry']], 'epsg:4326', c.geometry).to_crs(3174)
     
#base = c_r.plot(color='blue')
#c_p.plot(ax=base, color='red', markersize=7)