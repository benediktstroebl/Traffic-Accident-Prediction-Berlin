import pandas as pd
import os

#training data
path = os.getcwd()
df = pd.read_csv(path + "/data/full_sample.csv")

train = df[df["year"] != 2020]
test = df[df["year"] == 2020]

#column selection
X = train.drop(columns=["collision", "year", "segment_id"], axis=1)
X = X.loc[:, ~X.columns.str.contains('^Unnamed')]

y = train["collision"].copy()

#test data
X_test = test.drop(columns=["collision", "year", "segment_id"], axis=1)
X_test = X_test.loc[:, ~X_test.columns.str.contains('^Unnamed')]
y_test = test["collision"].copy()


#logit baseline - to check
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

X_baseline = X[['hour_cos', 'hour_sin', 'month_cos', 'month_sin','collision_cnt']]
lm_clf = LogisticRegression(solver='liblinear', C=10, random_state=0).fit(X_baseline, y)
y_predict_lm = lm_clf.predict(X_baseline)
print("Accuracy (logit baseline):", metrics.accuracy_score(y, y_predict_lm),
      "Precision (logit baseline)", metrics.precision_score(y, y_predict_lm),
      "Recall (logit baseline):", metrics.recall_score(y, y_predict_lm))

####XGboost grid search
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn import metrics

#plot function, code adapted from: https://stackoverflow.com/questions/37161563/how-to-graph-grid-scores-from-gridsearchcv
def plot_search_results(grid, title):
    """
    Params:
        grid: A trained GridSearchCV object.
    """
    ## Results from grid search
    results = grid.cv_results_
    means_test = results['mean_test_score']
    stds_test = results['std_test_score']

    ## Getting indexes of values per hyper-parameter
    masks=[]
    masks_names= list(grid.best_params_.keys())
    for p_k, p_v in grid.best_params_.items():
        masks.append(list(results['param_'+p_k].data==p_v))

    params=grid.param_grid

    ## Ploting results
    fig, ax = plt.subplots(1,len(params),sharex='none', sharey='all',figsize=(20,5))
    fig.suptitle(title)
    fig.text(0.08, 0.5, 'Mean score', va='center', rotation='vertical')
    pram_preformace_in_best = {}
    for i, p in enumerate(masks_names):
        m = np.stack(masks[:i] + masks[i+1:])
        pram_preformace_in_best
        best_parms_mask = m.all(axis=0)
        best_index = np.where(best_parms_mask)[0]
        x = np.array(params[p])
        y_1 = np.array(means_test[best_index])
        e_1 = np.array(stds_test[best_index])
        ax[i].errorbar(x, y_1, e_1, linestyle='--', marker='o', label='test')
        ax[i].set_xlabel(p.upper())

    plt.show()

#Round 1 - max_depth and min_child weight
cv_params = {'max_depth': [1, 2, 3, 4, 5, 6], 'min_child_weight': [1, 2, 3, 4]} # parameters to be tried in the grid search
fix_params = {'learning_rate': 0.2, 'n_estimators': 100, "scale_pos_weight": 20, 'objective': 'binary:logistic'}   #other parameters, fixed for the moment
csv = GridSearchCV(xgb.XGBClassifier(**fix_params, seed=1505), param_grid=cv_params, scoring='average_precision', cv=5, verbose=3)

csv.fit(X, y)
csv.cv_results_
print("Best parameters:", csv.best_params_)
print("Best score:", csv.best_score_)

#save round 1 results:
grid_1 = pd.DataFrame({"param" : csv.cv_results_["params"], "mean_score" : csv.cv_results_["mean_test_score"] ,
                       "std_score" : csv.cv_results_["std_test_score"], "fit_time" : csv.cv_results_["mean_fit_time"]})
grid_1.to_csv("C:\python-projects\Tables\grid_search_1.csv")

#plot round 1 results:
plot_search_results(csv, "a) First grid search")
plt.savefig("C:\python-projects\Figures\Grid_search_1.png")   # save the figure to file
plt.close()

best_param_1 = {'max_depth': 1, 'min_child_weight': 1, 'scale_pos_weight': 20, 'learning_rate': 0.2, 'n_estimators': 100, 'objective': 'binary:logistic'}

###Round 2
cv_params = {"learning_rate": [0.01, 0.05, 0.1, 0.15, 0.2], "n_estimators": [50, 60, 70, 80, 90, 100, 110, 120, 130]}
fix_params = {'max_depth': 1, 'min_child_weight': 1, "scale_pos_weight": 20, 'objective': 'binary:logistic'}   #other parameters, fixed for the moment
csv_2 = GridSearchCV(xgb.XGBClassifier(**fix_params, seed=1505), param_grid=cv_params, scoring='average_precision', cv=5, verbose=3)

csv_2.fit(X, y)
csv_2.cv_results_
print("Best parameters:", csv_2.best_params_)
print("Best score:", csv_2.best_score_)

#save round 2 results:
grid_2 = pd.DataFrame({"param" : csv_2.cv_results_["params"], "mean_score" : csv_2.cv_results_["mean_test_score"] ,
                       "std_score" : csv_2.cv_results_["std_test_score"], "fit_time" : csv_2.cv_results_["mean_fit_time"]})
grid_2.to_csv("C:\python-projects\Tables\grid_search_2.csv")

#plot round 2
plot_search_results(csv_2, "b) Second grid search")
plt.savefig("C:\python-projects\Figures\Grid_search_2.png")   # save the figure to file
plt.close()

best_param_2 = {'max_depth': 1, 'min_child_weight': 2, 'scale_pos_weight': 20, 'learning_rate': 0.1, 'n_estimators': 110, 'objective': 'binary:logistic'}

#Round 3
cv_params = {"scale_pos_weight" : [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
fix_params = {'max_depth': 1, 'min_child_weight': 2, 'learning_rate': 0.1,
              'n_estimators': 110, 'objective': 'binary:logistic'}  #other parameters, fixed for the moment
csv_3 = GridSearchCV(xgb.XGBClassifier(**fix_params, seed=1505), param_grid=cv_params, scoring='average_precision', cv=5, verbose=3)

csv_3.fit(X, y)
csv_3.cv_results_
print("Best parameters:", csv_3.best_params_)
print("Best score:", csv_3.best_score_)

#save round 3 results:
grid_3 = pd.DataFrame({"param" : csv_3.cv_results_["params"], "mean_score" : csv_3.cv_results_["mean_test_score"] ,
                       "std_score" : csv_3.cv_results_["std_test_score"], "fit_time" : csv_3.cv_results_["mean_fit_time"]})
grid_3.to_csv("C:\python-projects\Tables\grid_search_3.csv")

####plot round 2
###plot_search_results(csv_3, "b) Second grid search")
###plt.savefig("C:\python-projects\Figures\Grid_search_2.png")   # save the figure to file
###plt.close()

best_param_3 = {'max_depth': 1, 'min_child_weight': 2, 'scale_pos_weight': 1, 'learning_rate': 0.1, 'n_estimators': 110, 'objective': 'binary:logistic'}


####fit and test

from sklearn.model_selection import cross_validate
xgb_final = xgb.XGBClassifier(**best_param_3)

cv_final = cross_validate(xgb_final, X, y, scoring=["precision", "recall", "roc_auc", "average_precision", "f1"], cv=5)

#prints cross-validated evaluation scores
for key in cv_final:
    print(key, cv_final[key].mean())

#normal test
xgb_final.fit(X, y)
y_predict_xgb = xgb_final.predict(X) #on the train data

xgb.plot_importance(xgb_final)
plt.figure(figsize = (16, 12))
plt.show()
plt.close()

#train data
print("Precision XGB:", metrics.precision_score(y, y_predict_xgb))
print("Recall XGB:", metrics.recall_score(y, y_predict_xgb))
print("ROC_AUC XGB:",metrics.roc_auc_score(y, y_predict_xgb))
print("PR_ROC XGB:", metrics.average_precision_score(y, y_predict_xgb))

#test data
y_predict_test = xgb_final.predict(X_test)

print("Precision XGB:", metrics.precision_score(y_test, y_predict_test))
print("Recall XGB:", metrics.recall_score(y_test, y_predict_test))
print("ROC_AUC XGB:",metrics.roc_auc_score(y_test, y_predict_test))
print("PR_ROC XGB:", metrics.average_precision_score(y_test, y_predict_test))