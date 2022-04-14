"""
Tag collision points to road segments
"""
import os
import sys
import pandas as pd
import glob
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import fiona
from shapely.geometry import shape, Point, LineString
import pyproj

#sys.path.append(os.getcwd() + "/Machine-Learning-Project-Group-F/codes")
#from prep_collisions import df_to_gdf

#%%
path = os.getcwd()

def df_to_gdf(df, projection, geometry):
    crs = {'init': projection}
    gdf = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
    return gdf

#%%
def point_to_segment(gdf_point, gdf_segment, buffer):  
    """
    Tags collision points to road segments

    Parameters
    ----------
    point : GeoDataFrame
        A GeoDataFrame containing points of collisions
    segment : GeoDataFrame
        A GeoDataFrame containing detailed road segments
    buffer : numeric
        Distance in meters that adjusts the geometries of the points

    Returns
    -------
    col_road : GeoDataFrame
        A GeoDataFrame with matched collision points to road segments

    """
    # project to use meters in buffer
    col_data = gdf_point[['col_id','street','geometry']].to_crs(epsg=3174)
    road_data = gdf_segment[['segment_id','bezirk', 'stadtteil', 'strassenna','geometry']].to_crs(epsg=3174)
    
    # set buffer to 150 meters - to avoid NaN values, set higher buffer, likely more intersect/ roads tagged
    col_data['geometry'] = col_data.geometry.buffer(buffer)
    
    # find intersection of points and line segments
    intersect_data = gpd.sjoin(col_data, road_data, how='left', predicate = "intersects")
    
    # create final dataset with the two geometries
    col_road = gdf_point[['col_id','street', 'year', 'month', 'weekday', 'hour', 'geometry']].merge(intersect_data[['col_id','segment_id']],  on=['col_id'], how='left')
    col_road = gpd.GeoDataFrame(col_road.merge(road_data.to_crs(4326), on=['segment_id'], how='left'))
    
    # add distance
    p = df_to_gdf(col_road[['col_id', 'geometry_x']], 'epsg:4326', col_road.geometry_x).to_crs(3174)
    r = df_to_gdf(col_road[['segment_id', 'geometry_y']], 'epsg:4326', col_road.geometry_y).to_crs(3174)
    col_road['distance'] = p.distance(r)

    return col_road

#%%    
def plot_test(gdf, distance, street_name, segment_id = None): # choose only one bw street_name and segment_id
    p = df_to_gdf(gdf[['col_id', 'geometry_x']], 'epsg:4326', gdf.geometry_x).to_crs(3174)
    r = df_to_gdf(gdf[['segment_id', 'geometry_y']], 'epsg:4326', gdf.geometry_y).to_crs(3174) 
    col_road['distance'] = p.distance(r)
    
    c = gdf[gdf['distance'] > distance]
    
    #c = c[c['street'] == street_name]
    #c = c[c['segment_id'] == segment_id] 
    
    if street_name == None:
        c = c[c['segment_id'] == segment_id] 
    else:
        segment_id == None
        c = c[c['street'] == street_name]

    c_p = df_to_gdf(c[['col_id', 'geometry_x']], 'epsg:4326', c.geometry_x).to_crs(3174)
    c_r = df_to_gdf(c[['segment_id', 'geometry_y']], 'epsg:4326', c.geometry_y).to_crs(3174)
        
    # plot tests
    base = c_r.plot(alpha = 0.7)
    intersect_plot = c_p.plot(ax=base, color='red', markersize=7, alpha = 0.9)
    return intersect_plot
#%%
collisions_shp = gpd.read_file(path + "/data/output/collisions_shp.shp")
road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")

#%%
collisions_shp.info()
road_shp.info()

#%% save plots
collisions_shp.plot(color="red", markersize = 0.1, alpha = 0.3)

collisions_shp[collisions_shp['year']=="2018"].plot(color="red", markersize = 0.1)
collisions_shp[collisions_shp['year']=="2019"].plot(color="red", markersize = 1)
collisions_shp[collisions_shp['year']=="2020"].plot(color="red", markersize = 1)

road_shp.plot(markersize = 0.001, alpha = 0.3)


#%%    
col_road = point_to_segment(collisions_shp, road_shp, 20)    
col_road.segment_id.isna().sum()  # 51 missing matched using 20 buffer

col_road.groupby(['segment_id'])['col_id'].nunique().reset_index()

col_road['segment_id'].value_counts()
col_road['col_id'].value_counts()

col_road2 = point_to_segment(collisions_shp, road_shp, 2)  

col_road3 = point_to_segment(collisions_shp, road_shp, 10)  


#%%
# Plot random tests
streets = col_road.groupby(['segment_id'])['col_id'].nunique().reset_index().sort_values(by = ['col_id'], ascending = False)
plot_test(gdf = col_road, distance = 0, street_name = None, segment_id = 39275.0)
plot_test(gdf = col_road, distance = 19, street_name = None, segment_id = 39275.0)

#%%
streets = col_road.groupby(['street'])['col_id'].nunique().reset_index().sort_values(by = ['col_id'], ascending = False)

plot_test(gdf = col_road, distance = 0, street_name = "Alt-Kaulsdorf")

plot_test(gdf = col_road3, distance = 0, street_name = "Alt-Kaulsdorf")


plot_test(gdf = col_road2, distance = 0, street_name = "Alt-Kaulsdorf")




#%%
# Change buffer to 51 unmatched - append back to col_road
col_road_na = col_road[col_road.segment_id.isna()].iloc[:, 0:7]
col_road_na = df_to_gdf(col_road_na , 'epsg:4326', col_road_na.geometry_x)
col_road4 = point_to_segment(col_road_na, road_shp, 30) 
col_road4.segment_id.isna().sum() # 15 missing using 30 buffer

#%%
streets2 = col_road4.groupby(['street'])['col_id'].nunique().reset_index().sort_values(by = ['col_id'], ascending = False)
plot_test(col_road4, 0, "Alexanderplatzviertel")

plot_test(col_road4, 0, "Königin-Elisabeth-Straße")



streets_na = col_road_na.groupby(['street'])['col_id'].nunique().reset_index().sort_values(by = ['col_id'], ascending = False)

#%%
streets2 = col_road2.groupby(['segment_id'])['col_id'].nunique().reset_index().sort_values(by = ['col_id'], ascending = False)
plot_test(col_road2, 0, None, 6730)

#%%
###############################################################################
# Save GeoDataFrame - with 51 unmatched
col_road_fin = pd.DataFrame(col_road)
col_road_fin.drop(['geometry_x', 'geometry_y'], axis=1, inplace=True) 
col_road_fin.to_csv(path + "/data/output/collisions_road.csv", index = False)
#%%






