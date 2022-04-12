"""
Prepare collisions data from 2018-2020
"""

import pandas as pd
import geopandas as gpd
import glob
import os

path = os.getcwd()

def df_to_gdf(df, projection, geometry):
    crs = {'init': projection}
    gdf = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
    return gdf

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


# Create the shapefiles
# unique objectid - 33003 rows must check further
# they are unique! take into account year var
collisions.col_id.value_counts()
collisions.groupby(['col_id', 'year']).ngroups

# geometry - latitude 13, longitude 50
collisions.XGCSWGS84 = collisions.XGCSWGS84.astype('str').str.replace(',','.').astype('float64')
collisions.YGCSWGS84 = collisions.YGCSWGS84.astype('str').str.replace(',','.').astype('float64')
collisions_gdf = gpd.GeoDataFrame(collisions, geometry=gpd.points_from_xy(collisions.XGCSWGS84, collisions.YGCSWGS84))

collisions_shp = df_to_gdf(collisions_gdf, 'epsg:4326', collisions_gdf.geometry)

# drop 1 row
collisions_shp[collisions_shp.YGCSWGS84<50].col_id #lon = 1, drop
collisions_shp[collisions_shp.YGCSWGS84<50].geometry
collisions_shp.drop(collisions_shp[collisions_shp.YGCSWGS84==1].index, inplace = True)
collisions_shp.plot(color="red")

# Save collisions dataframe
collisions.to_csv(path + "/data/output/collisions.csv", index = False)
collisions_shp.to_file(path + "/data/output/collisions_shp.shp", index = False)
