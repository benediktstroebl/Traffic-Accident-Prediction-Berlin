import pandas as pd
import glob
import os
import geopandas as gpd
import folium
import matplotlib.pyplot as plt

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
collisions.rename(columns = {'BEZ':'DISTRICT', 'STRASSE':'STREET',
                       'UJAHR':'YEAR', 'UMONAT':'MONTH',
                       'USTUNDE':'HOUR', 'UWOCHENTAG  ':'WEEKDAY',
                       'UKATEGORIE':'ACC_CAT',
                       'UART':'ACC_TYPE1',
                       'UTYP1':'ACC_TYPE2',
                       'ULICHTVERH':'LIGHT_RATIO',
                       'IstRad':'BIKE',
                       'IstPKW':'CAR',
                       'IstFuss':'FOOT',
                       'IstKrad':'MOTOR',
                       'IstGkfz':'VEHICLE',
                       'IstSonstige':'OTHER',
                       'USTRZUSTAND':'ROAD_CON'}, inplace = True)

collisions.to_csv(path + "/data/output/collisions.csv")

#%%
# Create the shapefiles
# unique objectid - 33003 rows must check further
collisions.OBJECTID.value_counts()

# geometry - latitude 13, longitude 50
collisions.XGCSWGS84 = collisions.XGCSWGS84.astype('str').str.replace(',','.').astype('float64')
collisions.YGCSWGS84 = collisions.YGCSWGS84.astype('str').str.replace(',','.').astype('float64')
collisions_gdf = gpd.GeoDataFrame(collisions, geometry=gpd.points_from_xy(collisions.XGCSWGS84, collisions.YGCSWGS84))
collisions_gdf.head()

crs = {'init': 'epsg:4326'}
collisions_shp = gpd.GeoDataFrame(collisions_gdf, crs = crs, geometry = collisions_gdf.geometry)

# drop 1 row
collisions_shp[collisions_shp.YGCSWGS84<50].OBJECTID #lon = 1, drop
collisions_shp.drop(collisions_shp[collisions_shp.YGCSWGS84==1].index, inplace = True)
collisions_shp.plot(color="red")

collisions_shp.to_file(path + "/data/output/collisions_shp.shp")

# detailed road network
road_gdf = gpd.read_file(path + '/data/raw/road network/shp/Detailnetz-Strassenabschnitte.shp')
road_gdf.info()
road_gdf.head()
road_shp = road_gdf.to_crs(4326)
road_shp.plot()

road_shp.to_file(path + "/data/output/road_shp.shp")


#%%
# Intersection of collision points and road segments
collisions_shp = gpd.read_file(path + "/data/output/collisions_shp.shp")
road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")

#road_line = road_shp.geometry.unary_union

#trial join
col_road_shp = collisions_shp.sjoin(road_shp, how = 'left', predicate ='intersects')


samp = collisions_shp[collisions_shp.STREET == "Ackerstraße"]
samp.geometry = samp.geometry.buffer(5)

samp2 = samp.sjoin(road_shp, how = 'left', predicate = 'intersects')

samp3 = samp2[:10]
