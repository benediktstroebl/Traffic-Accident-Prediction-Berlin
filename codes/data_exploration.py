"""
Data exploration

"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas as gpd

#figure settings
mpl.rc('axes', labelsize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

#pycharm output settings
width = 320
pd.set_option('display.width', width)
#np.set_printoption(linewidth=width)
pd.set_option('display.max_columns', 10)

#loading data
path = os.getcwd()
train = pd.read_csv(path + "/data/train_data_big.csv")
#full = pd.read_csv(path + "/data/full_data_big.csv")


#quick look
train.head()
train.info()
train.describe()

#accident count per road segment
accident_segment = train[train["collision"] == 1].groupby(["segment_id"])["collision"].value_counts()#.reset_index()
accident_segment = pd.DataFrame(accident_segment)
accident_segment.rename(columns={ accident_segment.columns[0]: "accident_no" }, inplace=True)
accident_segment = accident_segment.reset_index()
accident_segment.sort_values(["accident_no"], ascending=False)

#categorical data
train["collision"].value_counts()
train["day"].value_counts()
train.groupby(["day"])["collision"].value_counts()
train.groupby(["day"])["collision"].value_counts(normalize=True)

#correlation matrix
from pandas.plotting import scatter_matrix

train = train.merge(accident_segment[["segment_id", "accident_no"]], how="left", on="segment_id")

cor_matrix = train.corr()
cor_matrix["collision"].sort_values(ascending=False)

#histograms
best = ["accident_no", "sun_elevation_angle", "temperature", "humidity", "hour_cos"]

train.hist(column=best)
plt.show()
plt.close()

#segment plot
segments = pd.read_csv(path + "/data/road_segments.csv")
segments_plot = segments.merge(accident_segment[["segment_id", "accident_no"]], left_on="segment_id", right_on="segment_id", how="left")

from shapely import wkt

segments_plot['geometry'] = segments_plot['geometry'].apply(wkt.loads)
segments_gdf = gpd.GeoDataFrame(segments_plot, crs='epsg:3174')

max = segments_gdf.nlargest(300, "accident_no")

fig, axs = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=(15,15))
axs[0].set_title("Road segments with the highest number of accidents")
axs[1].set_title("Road segments with no accidents")
segments_gdf.nlargest(1500, "accident_no").plot(ax=axs[0], color="red", markersize=0.2, alpha=0.3)
segments_gdf.nsmallest(1500, "accident_no").plot(ax=axs[1], color="blue", markersize=0.2, alpha=0.3)
plt.show()
plt.close()




