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

# return the midpoint of a segment
road_gdf['midpoint'] = road_gdf.centroid 

# merge with road width
road_width = pd.read_csv(path + "/data/output/road_width.csv")
road_gdf = road_gdf.merge(road_width, how="left", on = "segment_id")

road_shp = road_gdf.to_crs(4326)
#%%
# Save
road_gdf.to_csv(path + "/data/output/road_segments.csv", index = False)

#road_shp = road_gdf.to_crs(4326)
#road_shp.drop(['midpoint'], axis=1, inplace=True) # saving to shapefile only takes 1 geom
#road_shp.to_file(path + "/data/output/road_shp.shp", index = False)



road_shp.drop(['geometry'], axis=1, inplace=True) # saving to shapefile only takes 1 geom
road_shp = road_shp.set_geometry(road_shp['midpoint'])

road_shp.rename(columns = {'midpoint':'geometry'}, inplace = True)
road_shp = road_shp.iloc[:,0:19]

road_shp = gpd.GeoDataFrame(road_shp.set_geometry(road_shp['midpoint']))

road_shp.to_file(path + "/data/output/road_shp2.shp", index = False)

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