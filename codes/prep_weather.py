#loading packages

import pandas as pd
import geopandas as gpd

#loading data

path = "./data/temperature.csv"
temperature_df = pd.read_csv(path)


path = "./data/collisions_shp.shp"
