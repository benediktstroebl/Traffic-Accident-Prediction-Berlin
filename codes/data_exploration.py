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

#training data
path = os.getcwd()
df = pd.read_csv(path + "/data/full_sample.csv")
train = df[df["year"] != 2020]

#quick look
train.head()
train.info()
describe = train.describe().round(3)
describe = describe.T
#describe.to_csv("C:\python-projects\Tables\descriptive.csv")


#categorical data
train["collision"].value_counts()
train["weekday"].value_counts()
train.groupby(["weekday"])["collision"].value_counts()
train.groupby(["weekday"])["collision"].value_counts(normalize=True)

#correlation matrix

cor_matrix = train.corr()
cor_matrix["collision"].sort_values(ascending=False)

#histograms
best = ["collision_cnt", "sun_elevation_angle", "temparature", "visibility", "humidity", "prec_height", "prec_duration", "side_strt"]

#train.hist(column=best)

train_all = train.loc[:, ~train.columns.str.contains('^Unnamed')]
train_all = train_all.drop(columns=["segment_id", "year"], axis=1)
train_all.rename(columns={"temparature": "temperature"}, errors="raise")
train_all.hist()
plt.savefig("C:\python-projects\Figures\histograms.png")
plt.show()
plt.close()

#segment plot
segments = pd.read_csv(path + "/data/road_segments.csv")

collision_cnt = train.groupby(["segment_id"])[["collision_cnt"]].median() #to get number of collisions per segment
#collision_cnt.rename(columns={accident_segment.columns[0]: "collision_cnt" }, inplace=True)
collision_cnt = collision_cnt.reset_index()

segments_plot = segments.merge(collision_cnt[["segment_id", "collision_cnt"]], left_on="segment_id", right_on="segment_id", how="left")

from shapely import wkt

segments_plot['geometry'] = segments_plot['geometry'].apply(wkt.loads)
segments_gdf = gpd.GeoDataFrame(segments_plot, crs='epsg:3174')

fig, axs = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=(10,10))
#axs[0].set_title("Road segments with the highest number of accidents (n=1300)")
#axs[1].set_title("Road segments with no accidents (n=1300, random selection)")
segments_gdf.nlargest(1300, "collision_cnt").plot(ax=axs[0], color="red", markersize=0.2, alpha=0.8)
segments_gdf[segments_gdf["collision_cnt"] == 0].sample(n=1300, random_state=1505).plot(ax=axs[1], color="blue", markersize=0.4, alpha=0.8)
#plt.savefig("C:\python-projects\Figures\segments.png")
plt.show()
plt.close()





