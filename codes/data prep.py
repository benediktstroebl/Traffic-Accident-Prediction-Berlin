import pandas as pd
import glob
import os
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import fiona
from shapely.geometry import shape, Point, LineString
import pyproj

#%%
# Collisions data
path = os.getcwd()
all_files = glob.glob(path + "/data/raw/collisions/*.csv")

li = []

for file in all_files:   
    df = pd.read_csv(file, sep = ';', header = None, 
                                encoding='ISO-8859-1')
    df, df.columns = df[1:] , df.iloc[0]
    df.rename(columns = {'IstSonstig':'IstSonstige',
                         'STRZUSTAND':'USTRZUSTAND'}, inplace = True)
    li.append(df)

collisions = pd.concat(li, axis=0, ignore_index=True)
collisions.rename(columns = {
                        'OBJECTID':'objectid', 'LAND':'land',
                        'BEZ':'district', 'STRASSE':'street',
                       'UJAHR':'year', 'UMONAT':'month',
                       'USTUNDE':'hour', 'UWOCHENTAG':'weekday',
                       'UKATEGORIE':'acc_cat',
                       'UART':'acc_type1',
                       'UTYP1':'acc_type2',
                       'ULICHTVERH':'lightratio',
                       'IstRad':'bike',
                       'IstPKW':'car',
                       'IstFuss':'foot',
                       'IstKrad':'motor',
                       'IstGkfz':'vehicle',
                       'IstSonstige':'other',
                       'USTRZUSTAND':'road_con'}, inplace = True)

collisions = collisions.reset_index()  
collisions.rename(columns = {'index':'col_id'}, inplace = True)

collisions.to_csv(path + "/data/output/collisions.csv", index = False)

#%%
# Create the shapefiles
# unique objectid - 33003 rows must check further
# they are unique! take into account year var
collisions.col_id.value_counts()
collisions.groupby(['col_id', 'year']).ngroups

# geometry - latitude 13, longitude 50
collisions.XGCSWGS84 = collisions.XGCSWGS84.astype('str').str.replace(',','.').astype('float64')
collisions.YGCSWGS84 = collisions.YGCSWGS84.astype('str').str.replace(',','.').astype('float64')
collisions_gdf = gpd.GeoDataFrame(collisions, geometry=gpd.points_from_xy(collisions.XGCSWGS84, collisions.YGCSWGS84))
collisions_gdf.head()

crs = {'init': 'epsg:4326'}
collisions_shp = gpd.GeoDataFrame(collisions_gdf, crs = crs, geometry = collisions_gdf.geometry)

# drop 1 row
collisions_shp[collisions_shp.YGCSWGS84<50].col_id #lon = 1, drop
collisions_shp[collisions_shp.YGCSWGS84<50].geometry
collisions_shp.drop(collisions_shp[collisions_shp.YGCSWGS84==1].index, inplace = True)
collisions_shp.plot(color="red")

collisions_shp.to_file(path + "/data/output/collisions_shp.shp", index = False)

# detailed road network
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


#%%
# Intersection of collision points and road segments
collisions_shp = gpd.read_file(path + "/data/output/collisions_shp.shp")
road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")

collisions_shp.info()
road_shp.info()

###############################################################################
# TRIAL for a subset of data
###############################################################################
streets = collisions_shp.groupby(['land', 'district', 'street'])[ 'col_id'].nunique().reset_index()
samp = collisions_shp[collisions_shp.street == "Alt-Kaulsdorf"][['col_id','street','geometry']]

roads = road_shp.groupby(['bezirk', 'stadtteil', 'strassenna'])[ 'segment_id'].nunique().reset_index()
roads[roads['stadtteil'].str.contains("Kaulsdorf")]

road_shp['stadtteil'] = road_shp['stadtteil'].astype('str')
r_samp = road_shp[road_shp['stadtteil'].str.contains("Kaulsdorf")][['segment_id','bezirk', 'stadtteil', 'strassenna','geometry']]

# 1 project to use meters in buffer
samp = samp.to_crs(epsg=3174)
r_samp = r_samp.to_crs(epsg=3174)

# 2 plot in Kaulsdorf
base = r_samp.plot(color='blue')
samp.plot(ax=base, color='red', markersize=7)

# 3 set buffer to X meters
samp['geometry'] = samp.geometry.buffer(1.8)
#samp = samp.set_geometry(samp['geometry_2'])

# 4 get intersection of points and lines
# note: collisions tagged to more than 1 road segment may
# happened along road intersection. see example plot below
intersection = gpd.sjoin(samp, r_samp, how='left', predicate = "intersects")

# 5 select segments where intersections for plot
l1 = r_samp.merge(intersection.segment_id, on=['segment_id'], how='inner')

# 6 verify and plot points on tagged lines
base = l1.plot(color='blue')
samp = collisions_shp[collisions_shp.street == "Alt-Kaulsdorf"][['col_id','street','geometry']]
samp = samp.to_crs(epsg=3174)
samp.plot(ax=base, color='red', markersize=7)

# 6 create final dataset with the two geometries
subset = intersection[['col_id','segment_id']].merge(samp, on=['col_id'], how='inner')
subset = subset.merge(r_samp, on=['segment_id'], how='inner')

###############################################################################
# APPLY working code to whole data
###############################################################################
col_data = collisions_shp[['col_id','street','geometry']]
road_data = road_shp[['segment_id','bezirk', 'stadtteil', 'strassenna','geometry']]

# 1 project to use meters in buffer
col_data = col_data.to_crs(epsg=3174)
road_data = road_data.to_crs(epsg=3174)

# 2 plot in Kaulsdorf
base = road_data.plot(color='blue')
col_data.plot(ax=base, color='red', markersize=7)

# 3 set buffer to 150 meters - to avoid NaN values, set higher buffer, likely more intersect/ roads tagged
col_data['geometry'] = col_data.geometry.buffer(150)

# 4 get intersection of points and lines
# note: collisions tagged to more than 1 road segment may
# happened along road intersection. see example plot below
intersect_data = gpd.sjoin(col_data, road_data, how='left', predicate = "intersects")
intersect_data.segment_id.isna().sum()  

# 5 select segments where intersections for plot
segment_tag = road_data.merge(intersect_data.segment_id, on=['segment_id'], how='inner')

# 6 verify and plot points on tagged lines
base = segment_tag.plot(color='blue')
col_data = collisions_shp[['col_id','street','geometry']]
col_data = col_data.to_crs(epsg=3174)
col_data.plot(ax=base, color='red', markersize=7)

# back to 4326 crs projection
col_data = col_data.to_crs(epsg=4326)
road_data = road_data.to_crs(epsg=4326)

# 6 create final dataset with the two geometries
col_road = col_data.merge(intersect_data[['col_id','segment_id']],  on=['col_id'], how='left')
col_road = col_road.merge(road_data, on=['segment_id'], how='left')
col_road = gpd.GeoDataFrame(col_road)

col_road.drop(['geometry_x', 'geometry_y'], axis=1, inplace=True)

col_road.to_csv(path + "/data/output/collisions_road.csv", index = False)

# check dups
col_road.col_id.nunique() #38851 unique collision id
col_road.segment_id.nunique() #33050 unique segment id

col_road.groupby('col_id')['year'].nunique()



#### end
###############################################################################
# trial loop - nope
###############################################################################
#join = gpd.sjoin(lines_gdf, points_gdf, how = 'inner', op ='intersects')

# intersects
for i, point in enumerate(samp.geometry_2):   
    for j, line in enumerate(r_samp.geometry):
        #if line.intersects(point)==False:
         #   print(False)
        if line.contains(point):
            samp['segment_id'].iloc[i] = r_samp['segment_id'].iloc[j]
        else:
            samp['segment_id'].iloc[i] = "None"

print(samp['segment_id'])

   
