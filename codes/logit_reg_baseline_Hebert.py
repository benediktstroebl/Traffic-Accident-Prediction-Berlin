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
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_score, recall_score, PrecisionRecallDisplay, f1_score, precision_recall_curve


path = os.getcwd()

# trial data - collisions using "car" as outcome, others as regressors
# change data here (trial only below)

df = pd.read_csv(path + "/data/output/full_sample_big.csv")
df.rename(columns = {'weekday':'day'}, inplace = True)
df = df.reset_index()  
df.rename(columns = {'index':'idm'}, inplace = True)

# weather data - 
df_p = pd.read_csv(path + "/data/output/full_sample_big_precipitation.csv").iloc[:,1:8]
df_p = df_p.reset_index()  
df_p.rename(columns = {'index':'idm'}, inplace = True)

df_t = pd.read_csv(path + "/data/output/full_sample_big_temperature.csv").iloc[:,1:8]
df_t = df_t.reset_index()  
df_t.rename(columns = {'index':'idm'}, inplace = True)

df_v = pd.read_csv(path + "/data/output/full_sample_big_visibility.csv").iloc[:,1:7]
df_v = df_v.reset_index()  
df_v.rename(columns = {'index':'idm'}, inplace = True)

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
df_w = df_p.merge(df_t, how = "left", on = ['idm','segment_id', 'year', 'month', 'day', 'hour']).merge(df_v, how = "left", on = ['idm','segment_id', 'year', 'month', 'day', 'hour'])
# merge weather with sun elevation
df_full = df.merge(df_w, how = "left", on = ['idm','segment_id', 'year', 'month', 'day', 'hour'])

# merge with road data
data2 = df_full.merge(road2, how = "left", on = "segment_id")

data2.drop(['Unnamed: 0'], axis=1, inplace=True)
#%%
data2 = data2.dropna()
data2 = data2.merge(count_df, how = "left", on = ['segment_id', 'year'])   
     
data2.to_csv(path + "/data/output/full_data_big.csv", index = False)

#%%
# categorical variables - dummies generate
#cat = ['year']
cat = ['year', 'month', 'day', 'hour']
for c in cat:
    data2[c] = data2[c].astype("category")

for var in cat:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(data2[var], prefix=var)
    data2=data2.join(cat_list)
    #data2=data3

#%% save train and test
data2['year'] = data2['year'].astype(int)
train2 = data2[data2.year < 2020]

train2.drop(['year', 'year_2020', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84'], axis=1, inplace = True)

#train2.to_csv(path + "/data/output/train_data_big.csv", index = False)

test2 = data2[data2.year == 2020]
test2.drop(['year', 'month', 'day', 'hour', 'idm', 'XGCSWGS84', 'YGCSWGS84'], axis=1, inplace = True)
#test2.to_csv(path + "/data/output/test_data_big.csv", index = False)

#%%
## setup train and test
#data['year'] = data['year'].astype(int)
#train = data[data.year < 2020]
#test = data[data.year == 2020]

#%%
# set up outcome and predictors
train2 = train2.dropna()

train_final_vars2=train2.columns.values.tolist()
y2=['collision']
col_X2=[i for i in train_final_vars2 if i not in y] # all other variables as predictors

Y2 = train2[y2]
X2 = train2[col_X2]
X2 = X2[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']]
#X.drop(['segment_id'], axis=1, inplace = True)
#X = X.iloc[:,0:12]


col_X2_test=[i for i in train_final_vars2 if i not in y] # all other variables as predictors

Y2_test = test2[y2]
X2_test = test2[col_X2]
X2_test = X2_test[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']]


#%%
#logistic regression
model2 = LogisticRegression(solver='liblinear', C=10, random_state=0).fit(X2_test, Y2_test)
model2
#%%
model2.classes_
#%%
model2.intercept_
#%%
model2.coef_
#%%
model2.predict_proba(X2_test)
#%%
test2['Y_hat'] = model2.predict(X2_test)
#%% # accuracy
print(model2.score(X2_test, Y2_test))
#%% ROC_AUC
print(roc_auc_score(Y2_test, model.decision_function(X2_test)))

#%% precision
print(precision_score(test2['collision'], test2['Y_hat']))
#%% recall
print(recall_score(test2['collision'], test2['Y_hat']))
#%% f1 score
print(f1_score(test2['collision'], test2['Y_hat']))

#%%
confusion_matrix(Y2_test, model2.predict(X2_test))
#%%
print(classification_report(Y2_test, model2.predict(X2_test)))

#%%
# predict probabilities - big
lr_probs2 = model2.predict_proba(X2_test)
# keep probabilities for the positive outcome only
lr_probs2 = lr_probs2[:, 1]
# predict class values
yhat2 = model.predict(X2)
lr_precision2, lr_recall2, _ = precision_recall_curve(Y2_test, lr_probs2)

#%%
# predict probabilities - small
lr_probs = model.predict_proba(X_test)
# keep probabilities for the positive outcome only
lr_probs = lr_probs[:, 1]
# predict class values
yhat = model.predict(X)
lr_precision, lr_recall, _ = precision_recall_curve(Y_test, lr_probs)

#small blue
#big orange
#%%


plt.plot(lr_recall, lr_precision, linestyle='-', label='Logit_IB_Small')
plt.plot(lr_recall2, lr_precision2, linestyle='-', label='Logit_IB_Hebert')
# axis labels
plt.xlabel('Recall')
plt.ylabel('Precision')
# show the legend
plt.legend(loc = "lower left")
# show the plot
plt.show()



pyplot.plot([0, 1], [no_skill, no_skill], linestyle='--', label='Logit_IB_Hebert')

