import pandas as pd
import os

#training data
path = os.getcwd()
train = pd.read_csv(path + "/data/train_data_big.csv")
train_na = train.dropna()

X = train_na.drop(columns=["collision", "year_2018", "year_2019", "segment_id"], axis=1)
y = train_na["collision"].copy()

#test data
test = pd.read_csv(path + "/data/test_data_big.csv").dropna()
X_test = test[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']].copy()
y_test = test["collision"].copy()

from sklearn.model_selection import train_test_split
X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.3, random_state=1505)

#ADA boost
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics

ada_clf = AdaBoostClassifier(
    DecisionTreeClassifier(max_depth=1), n_estimators=50,
    algorithm="SAMME.R", learning_rate=0.5, random_state=1505)
ada_clf.fit(X_train, y_train)
y_predict = ada_clf.predict(X_validate) #validation data
X_predict = ada_clf.predict(X_train) #training data

#training data
print("Accuracy:", metrics.accuracy_score(y_train, X_predict))
print("Recall:", metrics.recall_score(y_train, X_predict))

#validation data
print("Accuracy:", metrics.accuracy_score(y_validate, y_predict))
print("Recall:", metrics.recall_score(y_validate, y_predict))


ada_clf.score(X, y)

#accuracy
print(ada_clf.score(X, y))
#ROC_AUC
print(roc_auc_score(y, ada_clf.decision_function(X)))

#logit baseline - to check
from sklearn.linear_model import LogisticRegression
X_baseline = X[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']]
lm_clf = LogisticRegression(solver='liblinear', C=10, random_state=0).fit(X_baseline, y)
y_predict_lm = lm_clf.predict(X_baseline)
print("Accuracy (logit baseline):", metrics.accuracy_score(y, y_predict_lm),
      "Precision (logit baseline)", metrics.precision_score(y, y_predict_lm),
      "Recall (logit baseline):", metrics.recall_score(y, y_predict_lm))

####XGboost: logit baseline model
import xgboost as xgb
from sklearn.model_selection import GridSearchCV

#maximising recall score

#set folds?

#best params: depth: 3; child_weight: 1, scale_pos_weight: 5

#Round 1
cv_params = {'max_depth': [3, 6, 9], 'min_child_weight': [0.5, 1, 2], "scale_pos_weight" : [50, 100, 150]}    # parameters to be tries in the grid search
fix_params = {'learning_rate': 0.2, 'n_estimators': 100, 'objective': 'binary:logistic'}   #other parameters, fixed for the moment
csv = GridSearchCV(xgb.XGBClassifier(**fix_params, seed=1505), param_grid=cv_params, scoring='f1', cv=5, verbose=3)

csv.fit(X_baseline, y)
csv.cv_results_
print("Best parameters:", csv.best_params_)
print("F1:", csv.best_score_)

best_param_f_1 = {'max_depth': 3, 'min_child_weight': 2, 'scale_pos_weight': 50, 'learning_rate': 0.2, 'n_estimators': 100, 'objective': 'binary:logistic'}

#Round 2
cv_params = {"max_depth": [1, 2, 3, 4, 5], "scale_pos_weight": [30, 40, 50, 60, 70]}
fix_params = {'learning_rate': 0.2, 'n_estimators': 100, "min_child_weight": 2, 'objective': 'binary:logistic'}   #other parameters, fixed for the moment
csv = GridSearchCV(xgb.XGBClassifier(**fix_params, seed=1505), param_grid=cv_params, scoring='f1', cv=5, verbose=3)

csv.fit(X_baseline, y)
csv.cv_results_
print("Best parameters:", csv.best_params_)
print("F1:", csv.best_score_)

best_param_f_2 = {'max_depth': 1, 'min_child_weight': 2, 'scale_pos_weight': 30, 'learning_rate': 0.2, 'n_estimators': 100, 'objective': 'binary:logistic'}

#Round 3...

best_param_recall = {'max_depth': 3, 'min_child_weight': 1, 'scale_pos_weight': 150}
best_param_f1 = {'max_depth': 3, 'min_child_weight': 2, 'scale_pos_weight': 50, 'learning_rate': 0.2, 'n_estimators': 100, 'objective': 'binary:logistic'}
best_param_roc = {'max_depth': 3, 'min_child_weight': 1, 'scale_pos_weight': 150, 'learning_rate': 0.2, 'n_estimators': 100, 'objective': 'binary:logistic'}

####fit and test

#cross validation
data_dmatrix = xgb.DMatrix(data=X_baseline, label=y)
xgb_cv = xgb.cv(dtrain=data_dmatrix, params=best_param_f_2, nfold=3, num_boost_round=50,
            early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=1505)

#normal test
xgb_clf2 = xgb.XGBClassifier(**best_param_f_2)
xgb_clf2.fit(X_baseline, y)
y_predict_xgb = xgb_clf2.predict(X_baseline) #on the train data

xgb.plot_importance(xgb_clf2)
plt.figure(figsize = (16, 12))
plt.show()

#train data
print("Precision XGB:", metrics.precision_score(y, y_predict_xgb))
print("Recall XGB:", metrics.recall_score(y, y_predict_xgb))
print("ROC_AUC XGB:",metrics.roc_auc_score(y, y_predict_xgb))
