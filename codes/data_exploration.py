"""
Data exploration

"""

import pandas as pd
# geopandas as gpd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

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
train = pd.read_csv(path + "/data/train_data_small.csv")

full = pd.read_csv(path + "/data/full_data_small.csv")


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
best = ["collision", "accident_no", "sun_elevation_angle", "temperature", "humidity", "hour_cos"]

train.hist(column=best)
plt.show()

#scatter matrix
scatter_matrix(train[best], figsize=(12, 8))
plt.show()





