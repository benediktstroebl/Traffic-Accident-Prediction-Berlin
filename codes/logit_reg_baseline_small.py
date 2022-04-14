"""
Baseline model

Logistic regression
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
from sklearn.feature_selection import RFE
import statsmodels.api as sm

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

path = os.getcwd()

# trial data - collisions using "car" as outcome, others as regressors
# change data here (trial only below)

df1 = pd.read_csv(path + "/data/output/full_sample.csv")
df1.rename(columns = {'weekday':'day'}, inplace = True)
df1 = df1.reset_index()  
df1.rename(columns = {'index':'idm'}, inplace = True)

# weather data - 
df1_p = pd.read_csv(path + "/data/output/full_sample_precipitation.csv").iloc[:,1:8]
df1_p = df1_p.reset_index()  
df1_p.rename(columns = {'index':'idm'}, inplace = True)

df1_t = pd.read_csv(path + "/data/output/full_sample_temperature.csv").iloc[:,1:8]
df1_t = df1_t.reset_index()  
df1_t.rename(columns = {'index':'idm'}, inplace = True)

df1_v = pd.read_csv(path + "/data/output/full_sample_visibility.csv").iloc[:,1:7]
df1_v = df1_v.reset_index()  
df1_v.rename(columns = {'index':'idm'}, inplace = True)
#%%
road = pd.read_csv(path + "/data/output/road_segments.csv")
road2 = road[['segment_id', 'width1_m', 'length_m']]
road2.rename(columns = {'width1_m':'width',
                           'length_m':'length'}, inplace = True)

#%%
#df.groupby(['segment_id', 'year', 'month', 'day', 'hour'])['collision'].nunique().reset_index()
#df.groupby(['Unnamed: 0'])['collision'].nunique().reset_index()
#df_p.groupby(['segment_id', 'year', 'month', 'day', 'hour'])['Unnamed: 0'].nunique().reset_index()
#df_t.groupby(['segment_id', 'year', 'month', 'day', 'hour'])['Unnamed: 0'].nunique().reset_index()
#df_v.groupby(['segment_id', 'year', 'month', 'day', 'hour'])['Unnamed: 0'].nunique().reset_index()

# merge all weather factors
df1_w = df1_p.merge(df1_t, how = "left", on = ['idm','segment_id', 'year', 'month', 'day', 'hour']).merge(df1_v, how = "left", on = ['idm','segment_id', 'year', 'month', 'day', 'hour'])
# merge weather with sun elevation
df1_full = df1.merge(df1_w, how = "left", on = ['idm','segment_id', 'year', 'month', 'day', 'hour'])

data = df1_full.merge(road2, how = "left", on = "segment_id")

data.drop(['Unnamed: 0'], axis=1, inplace=True)
#%%

count2018 = pd.DataFrame(data[data['year']==2018].groupby(['segment_id'])['collision'].sum()).reset_index()
count2018['year'] = 2018

count2019 = pd.DataFrame(data[data['year']<=2019].groupby(['segment_id'])['collision'].sum()).reset_index()
count2019['year'] = 2019

count2020 = pd.DataFrame(data[data['year']<=2020].groupby(['segment_id'])['collision'].sum()).reset_index()
count2020['year'] = 2020

count_df = count2018.append(count2019).append(count2020)
count_df.rename(columns = {'collision':'collision_cnt'}, inplace=True)

#%%
data = data.dropna()
data = data.merge(count_df, how = "left", on = ['segment_id', 'year'])   

data.to_csv(path + "/data/output/full_data_small.csv", index = False)

#%%
# categorical variables - dummies generate
#cat = ['year']
cat = ['year', 'month', 'day', 'hour']
for c in cat:
    data[c] = data[c].astype("category")

for var in cat:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(data[var], prefix=var)
    data=data.join(cat_list)
    #data=data1

#%% save train and test
data['year'] = data['year'].astype(int)
train = data[data.year < 2020]
train.drop(['year', 'year_2020', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84'], axis=1, inplace = True)
train.to_csv(path + "/data/output/train_data_small.csv", index = False)
#train.drop(['year', 'year_2020', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84'], axis=1, inplace = True)

test = data[data.year == 2020]
#test.drop(['year', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84'], axis=1, inplace = True)

test.drop(['year', 'year_2020', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84'], axis=1, inplace = True)
test.to_csv(path + "/data/output/test_data_small.csv", index = False)

#%%
## setup train and test
#data['year'] = data['year'].astype(int)
#train = data[data.year < 2020]
#test = data[data.year == 2020]

#%%
# set up outcome and predictors
train_final_vars=train.columns.values.tolist()
y=['collision']
col_X=[i for i in train_final_vars if i not in y] # all other variables as predictors

Y = train[y]
X = train[col_X]
X = X[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']]

#X.drop(['segment_id'], axis=1, inplace = True)
#X.drop(['year', 'year_2020', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84', 'segment_id'], axis=1, inplace = True)

col_X_test=[i for i in train_final_vars if i not in y] # all other variables as predictors

Y_test = test[y]
X_test = test[col_X_test]
X_test = X_test[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']]

#%%
#logistic regression
model = LogisticRegression(solver='liblinear', random_state=0).fit(X_test, Y_test)
model
#%%
model.classes_
#%%
model.intercept_
#%%
model.coef_
#%%
model.predict_proba(X)
#%%
test['Y_hat'] = model.predict(X_test)
#%% # accuracy
print(model.score(X_test, Y_test))
#%% ROC_AUC
print(roc_auc_score(Y_test, model.decision_function(X_test)))
#%% precision
print(precision_score(test['collision'], test['Y_hat']))
#%% recall
print(recall_score(test['collision'], test['Y_hat']))
#%% f1 score
print(f1_score(test['collision'], test['Y_hat']))

#%%
confusion_matrix(Y_test, model.predict(X_test))
#%%
print(classification_report(Y_test, model.predict(X_test)))


