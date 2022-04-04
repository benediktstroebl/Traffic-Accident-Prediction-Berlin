# Tag collision points to road segments

import pandas as pd
import glob
import os
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import fiona
from shapely.geometry import shape, Point, LineString
import pyproj

path = os.getcwd()

collisions_shp = gpd.read_file(path + "/data/output/collisions_shp.shp")
road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")

collisions_shp.info()
road_shp.info()

def point_to_segment(point, segment, buffer):  
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
    col_data = point[['col_id','street','geometry']].to_crs(epsg=3174)
    road_data = segment[['segment_id','bezirk', 'stadtteil', 'strassenna','geometry']].to_crs(epsg=3174)
    
    # set buffer to 150 meters - to avoid NaN values, set higher buffer, likely more intersect/ roads tagged
    col_data['geometry'] = col_data.geometry.buffer(buffer)
    
    # find intersection of points and line segments
    intersect_data = gpd.sjoin(col_data, road_data, how='left', predicate = "intersects")
    
    # create final dataset with the two geometries
    col_road = point[['col_id','street','geometry']].merge(intersect_data[['col_id','segment_id']],  on=['col_id'], how='left')
    col_road = gpd.GeoDataFrame(col_road.merge(road_data.to_crs(4326), on=['segment_id'], how='left'))

    return col_road
    
col_road = point_to_segment(collisions_shp, road_shp, 20)    
col_road.segment_id.isna().sum()  
    
# Save GeoDataFrame
col_road.drop(['geometry_x', 'geometry_y'], axis=1, inplace=True)
col_road.to_csv(path + "/data/output/collisions_road.csv", index = False)
