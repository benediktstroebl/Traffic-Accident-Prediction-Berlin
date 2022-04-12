"""
Baseline model

Logistic regression
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm

path = os.getcwd()

# trial data - collisions using "car" as outcome, others as regressors
# change data here (trial only below)
collisions_shp = gpd.read_file(path + "/data/output/collisions_shp.shp")
var = ['year', 'month', 'weekday', 'hour']
for v in var:
    collisions_shp[v] = collisions_shp[v].astype(int)

road_shp =  gpd.read_file(path + "/data/output/road_shp.shp")
col_road = pd.read_csv(path + "/data/output/collisions_road.csv")

data = col_road.merge(collisions_shp, on = ['col_id','street', 'year', 'month', 'hour', 'weekday'], how = "left").merge(road_shp, on = ['segment_id', 'bezirk', 'stadtteil', 'strassenna'], how = "left")

data.groupby(['year'])['col_id'].nunique().reset_index()

cat = ['year', 'month', 'weekday', 'hour', 'car', 'acc_cat', 'acc_type1', 'acc_type2', 'lightratio', 'road_con']
for c in cat:
    data[c] = data[c].astype("category")
# other numeric variables: weather data, road length, road width

# select variable that will be used
data_select = pd.DataFrame(data[['col_id', 'segment_id', 'year', 'month', 'weekday', 'hour', 'car', 'acc_cat', 'acc_type1', 'acc_type2', 'lightratio', 'road_con', 'length_m']])
cat_vars = ['year', 'month', 'weekday', 'hour', 'acc_cat', 'acc_type1', 'acc_type2', 'lightratio', 'road_con']
for var in cat_vars:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(data_select[var], prefix=var)
    data1=data_select.join(cat_list)
    data_select=data1


data1['year'] = data['year'].astype(int)
train = data1[data1.year < 2020]
test = data1[data1.year == 2020]


train1 = train.drop(labels=cat_vars, axis=1)
train1 = train1.drop(labels = ['col_id', 'segment_id',  'year_2018', 'year_2019', 'year_2020'], axis=1)

# logreg only
# set up outcome and predictors
train_final_vars=train1.columns.values.tolist()
y=['car'] # change outcome variable here
col_X=[i for i in train_final_vars if i not in y] # all other variables as predictors

train1['length_m'] = np.log(train1['length_m'])  # transform road length to log
train1 = train1[train1['length_m'].notna()]


Y = train1['car']
X = train1[col_X]


############################## using statsmodel - returns ERROR!!!!!!
logit_model=sm.Logit(Y,X) 
result=logit_model.fit()
print(result.summary2())


LogisticRegression(random_state=0).fit(X, Y)



################################ using sklearn
# logreg and feature selection
logreg = LogisticRegression()

rfe = RFE(logreg, 69)
rfe = rfe.fit(X, Y.values.ravel())
print(rfe.support_)
print(rfe.ranking_)

