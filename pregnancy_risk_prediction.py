# -*- coding: utf-8 -*-
"""Pregnancy_Risk_Prediction

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WxB37PSeM3XXCFQLIA_4kLtPYeUch86x
"""

#Import library for ignoring warnings
import warnings
warnings.simplefilter(action="ignore")
warnings.filterwarnings("ignore")

#Import the necessary packages
import numpy as np
import pandas as pd

#Import librarires for Data Visualisation
import matplotlib.pyplot as plt
import seaborn as sns

#Algorithms
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import mean_squared_error
from sklearn.metrics import precision_recall_fscore_support

"""**MATERNAL HEALTH RISK DATA**"""

#Loading data into dataframe
df1 = pd.read_csv('/content/Maternal Health Risk Data Set.csv')

#Printing first five rows
df1.head()

#Checking information about data
df1.info()

#Printing size of dataset
print(f"Dataset size is: {df1.shape}")

#Counting the values of risk under RiskLevel column
print(df1["RiskLevel"].value_counts())

df1.describe().T

#Plot stacked histrogram for the feature variable
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(30,25))
risk_level_order = {"high risk","mid risk", "low risk"}

for ax, column in zip(axes.flatten(), df1.columns):
  sns.histplot(data =df1,
               x=column,
               kde=True,
               hue ="RiskLevel",
               hue_order = risk_level_order,
               multiple ="stack",
               palette={"low risk" : "green", "mid risk" : "orange", "high risk" : "red"},
               element = "bars", ax=ax)
  ax.set_title(f"{column}", fontsize =25)
plt.tight_layout()
plt.savefig("maternal_feature_description.png")
plt.show()

#Plot boxplots(for outliars) for the feature variables
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(20,15))

for ax, column in zip(axes.flatten(), df1.columns):
  sns.boxplot(y=df1[column],
              color ="blue",
              ax=ax)
  ax.set_title(f"{column}", fontsize=18)

plt.tight_layout()
plt.savefig("maternal_skewed_distribution_to_check_outliars.png")
plt.show()

"""Correlation Analysis of Variables"""

df1["RiskLevel"].value_counts()

#Mapping RiskLevel to integer values
risk_mapping = {"low risk" : 0, "mid risk" : 1, "high risk" : 2}
df1["RiskLevel"] = df1["RiskLevel"].map(risk_mapping)
df1.info()

#Create a correlation heatmap
plt.figure(figsize =(22,20))
sns.heatmap(df1.corr(), annot = True, cmap ="GnBu")
plt.title("Correlation Heatmap of Variables", fontsize = 16)
plt.savefig("maternal_heatmap_to_check_correlation.png")
plt.show()

#Create a pairplot with Risklevel
risk_colors = {0 : "green", 1 : "orange", 2 :"red"}

plot = sns.pairplot(df1, hue ="RiskLevel",
                    palette=risk_colors,
                    markers =["o","s","D"])
legend_labels = {"0" : "Low", "1" : "Mid", "2" : "High"}
for text, label in zip (plot._legend.texts,legend_labels.values()):
  text.set_text(label)
plt.savefig("maternal_pairplot_to_see_patterns.png")
plt.show()

#Drop SystolicBP for model training
df1 =df1.drop(["SystolicBP"], axis =1)

#Indentify the outlier in HeartRate
df1.HeartRate.sort_values().head()

df1 = df1.drop(df1.index[df1.HeartRate == 7])

df1.HeartRate.sort_values().head()

"""MODEL BUILDING"""

df1.info()

#Feature Scaling
columns = ['Age','DiastolicBP','BS','BodyTemp','HeartRate']
scale_X = StandardScaler()
X= pd.DataFrame(scale_X.fit_transform(df1.drop(['RiskLevel'], axis =1),), columns = columns)
Y=df1['RiskLevel']

X.head()

#train-test split
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size =0.2, random_state =42 , stratify = Y)
X_train.shape, X_test.shape, Y_train.shape,  Y_test.shape

"""**LOGISTIC REGRESSION**"""

# Baseline model of Logistic Regression
logistic_regression = linear_model.LogisticRegression()
logistic_regression_mod = logistic_regression.fit(X_train, Y_train)
print(f"Baseline Logistic Regression: {round(logistic_regression_mod.score(X_test, Y_test), 3)}")
pred_logistic_regression = logistic_regression_mod.predict(X_test)

# Cross validate Logistic Regression model
scores_Logistic = cross_val_score(logistic_regression, X_train, Y_train, cv=3, scoring="accuracy")
print(f"Scores(Cross validate) for Logistic Regression model:\n{scores_Logistic}")
print(f"CrossValMeans: {round(scores_Logistic.mean(), 3)}")
print(f"CrossValStandard Deviation: {round(scores_Logistic.std(), 3)}")

params_LR = {"tol": [0.0001,0.0002,0.0003],
            "C": [0.01, 0.1, 1, 10, 100],
            "intercept_scaling": [1, 2, 3, 4],
            "solver": ["liblinear", "lbfgs", "newton-cg"],
            "max_iter": [100, 200, 300],
              }

GridSearchCV_LR = GridSearchCV(estimator=linear_model.LogisticRegression(),
                                param_grid=params_LR,
                                cv=3,
                                scoring="accuracy",
                                return_train_score=True,
                                )

GridSearchCV_LR.fit(X_train, Y_train);

print(f"Best estimator for LR model:\n{GridSearchCV_LR.best_estimator_}")
print(f"Best parameter values for LR model:\n{GridSearchCV_LR.best_params_}")
print(f"Best score for LR model: {round(GridSearchCV_LR.best_score_, 3)}")

# Test with new parameter
logistic_regression = linear_model.LogisticRegression(C=0.01, intercept_scaling=1, max_iter=100, solver="liblinear", tol=0.0001, random_state=42)
logistic_regression_mod = logistic_regression.fit(X_train, Y_train)
pred_logistic_regression = logistic_regression_mod.predict(X_test)

mse_logistic_regression = mean_squared_error(Y_test, pred_logistic_regression)
rmse_logistic_regression = np.sqrt(mean_squared_error(Y_test, pred_logistic_regression))
score_logistic_regression_train = logistic_regression_mod.score(X_train, Y_train)
score_logistic_regression_test = logistic_regression_mod.score(X_test, Y_test)

print(f"Mean Square Error for Logistic Regression = {round(mse_logistic_regression, 3)}")
print(f"Root Mean Square Error for Logistic Regression = {round(rmse_logistic_regression, 3)}")
print(f"R^2(coefficient of determination) on training set = {round(score_logistic_regression_train, 3)}")
print(f"R^2(coefficient of determination) on testing set = {round(score_logistic_regression_test, 3)}")

print("Classification Report")
print(classification_report(Y_test, pred_logistic_regression))
print("Confusion Matrix:")
print(confusion_matrix(Y_test, pred_logistic_regression))

ax= plt.subplot()
sns.heatmap(confusion_matrix(Y_test, pred_logistic_regression), annot=True, ax=ax, cmap = "GnBu");

ax.set_xlabel("Predicted Risk Levels");
ax.set_ylabel("True Risk Levels");
ax.set_title("Confusion Matrix");
ax.xaxis.set_ticklabels(["Low", "Mid", "High"]);
ax.yaxis.set_ticklabels(["Low", "Mid", "High"]);

"""K-Nearest Neighbors"""

# Baseline model of K-Nearest Neighbors
knn = KNeighborsClassifier()
knn_mod = knn.fit(X_train, Y_train)
print(f"Baseline K-Nearest Neighbors: {round(knn_mod.score(X_test, Y_test), 3)}")
pred_knn = knn_mod.predict(X_test)

# Cross validate K-Nearest Neighbors model
scores_knn = cross_val_score(knn, X_train, Y_train, cv=3, scoring="accuracy")
print(f"Scores(Cross validate) for K-Nearest Neighbors model:\n{scores_knn}")
print(f"CrossValMeans: {round(scores_knn.mean(), 3)}")
print(f"CrossValStandard Deviation: {round(scores_knn.std(), 3)}")

params_knn = {"leaf_size": list(range(1,30)),
              "n_neighbors": list(range(1,21)),
              "p": [1,2],
              "weights": ["uniform", "distance"],
             }

GridSearchCV_knn = GridSearchCV(estimator=KNeighborsClassifier(),
                                param_grid=params_knn,
                                cv=3,
                                scoring="accuracy",
                                return_train_score=True
                                )

# Fit model with train data
GridSearchCV_knn.fit(X_train, Y_train);

print(f"Best estimator for KNN model:\n{GridSearchCV_knn.best_estimator_}")
print(f"Best parameter values:\n{GridSearchCV_knn.best_params_}")
print(f"Best score for GNB model: {round(GridSearchCV_knn.best_score_, 3)}")

# Test with new parameter
knn = KNeighborsClassifier(leaf_size=1, n_neighbors=10, p=2, weights="distance")
knn_mod = knn.fit(X_train, Y_train)
pred_knn = knn_mod.predict(X_test)

mse_knn = mean_squared_error(Y_test, pred_knn)
rmse_knn = np.sqrt(mean_squared_error(Y_test, pred_knn))
score_knn_train = knn_mod.score(X_train, Y_train)
score_knn_test = knn_mod.score(X_test, Y_test)

print(f"Mean Square Error for K_Nearest Neighbor  = {round(mse_knn, 3)}")
print(f"Root Mean Square Error for K_Nearest Neighbor = {round(rmse_knn, 3)}")
print(f"R^2(coefficient of determination) on training set = {round(score_knn_train, 3)}")
print(f"R^2(coefficient of determination) on testing set = {round(score_knn_test, 3)}")

print("Classification Report")
print(classification_report(Y_test, pred_knn))
print("Confusion Matrix:")
print(confusion_matrix(Y_test, pred_knn))

ax= plt.subplot()
sns.heatmap(confusion_matrix(Y_test, pred_knn), annot=True, ax = ax, cmap = "GnBu");

ax.set_xlabel("Predicted Risk Levels");
ax.set_ylabel("True Risk Levels");
ax.set_title("Confusion Matrix");
ax.xaxis.set_ticklabels(["Low", "Mid", "High"]);
ax.yaxis.set_ticklabels(["Low", "Mid", "High"]);

"""Random Forest"""

# Baseline model of Random Forest Classifier
random_forest = RandomForestClassifier()
random_forest_mod = random_forest.fit(X_train, Y_train)
print(f"Baseline Random Forest: {round(random_forest_mod.score(X_test, Y_test), 3)}")
pred_random_forest = random_forest_mod.predict(X_test)

# Cross validate Random Forest Classifier model
scores_RF = cross_val_score(random_forest, X_train, Y_train, cv=3, scoring = "accuracy")
print(f"Scores(Cross validate) for Random forest model:\n{scores_RF}")
print(f"CrossValMeans: {round(scores_RF.mean(), 3)}")
print(f"CrossValStandard Deviation: {round(scores_RF.std(), 3)}")

params_RF = {"min_samples_split": [2, 6, 20],
              "min_samples_leaf": [1, 2, 4],
              "n_estimators" :[50,100,200,300,400],
              "max_depth": [None, 10, 20, 30],
              "criterion": ["gini", "entropy"]
              }

GridSearchCV_RF = GridSearchCV(estimator=RandomForestClassifier(),
                                param_grid=params_RF,
                                cv=3,
                                scoring="accuracy",
                                return_train_score=True
                                )

GridSearchCV_RF.fit(X_train, Y_train);

print(f"Best estimator for RF model:\n{GridSearchCV_RF.best_estimator_}")
print(f"Best parameter values for RF model:\n{GridSearchCV_RF.best_params_}")
print(f"Best score for RF model: {round(GridSearchCV_RF.best_score_, 3)}")

# Test with new parameter
random_forest = RandomForestClassifier(criterion="entropy", max_depth=30, min_samples_leaf=1, min_samples_split=2, n_estimators=200, random_state=42)
random_forest_mod = random_forest.fit(X_train, Y_train)
pred_random_forest = random_forest_mod.predict(X_test)

mse_random_forest = mean_squared_error(Y_test, pred_random_forest)
rmse_random_forest = np.sqrt(mean_squared_error(Y_test, pred_random_forest))
score_random_forest_train = random_forest_mod.score(X_train, Y_train)
score_random_forest_test = random_forest_mod.score(X_test, Y_test)

print(f"Mean Square Error for Random Forest = {round(mse_random_forest, 3)}")
print(f"Root Mean Square Error for Random Forest = {round(rmse_random_forest, 3)}")
print(f"R^2(coefficient of determination) on training set = {round(score_random_forest_train, 3)}")
print(f"R^2(coefficient of determination) on testing set = {round(score_random_forest_test, 3)}")

print("Classification Report")
print(classification_report(Y_test, pred_random_forest))
print("Confusion Matrix:")
print(confusion_matrix(Y_test, pred_random_forest))

ax= plt.subplot()
sns.heatmap(confusion_matrix(Y_test, pred_random_forest), annot=True, ax = ax, cmap = "GnBu");

ax.set_xlabel("Predicted Risk Levels");
ax.set_ylabel("True Risk Levels");
ax.set_title("Confusion Matrix");
ax.xaxis.set_ticklabels(["Low", "Mid", "High"]);
ax.yaxis.set_ticklabels(["Low", "Mid", "High"]);

"""Gradient Boosting Classifier"""

# Baseline model of gradient boosting classifier
gbc = GradientBoostingClassifier()
gbc_mod = gbc.fit(X_train, Y_train)
print(f"Baseline gradient boosting classifier: {round(gbc_mod.score(X_test, Y_test), 3)}")
pred_gbc = gbc_mod.predict(X_test)

# Cross validate Gradient Boosting Classifier model
scores_GBC = cross_val_score(gbc, X_train, Y_train, cv=3, scoring = "accuracy")
print(f"Scores(Cross validate) for Gradient Boosting Classifier model:\n{scores_GBC}")
print(f"CrossValMeans: {round(scores_GBC.mean(), 3)}")
print(f"CrossValStandard Deviation: {round(scores_GBC.std(), 3)}")

params_GBC = {
    "loss": ["log_loss"],  # Change 'deviance' to 'log_loss'
    "learning_rate": [0.01, 0.05, 0.075, 0.1],
    "n_estimators": [100, 250, 500],
    "max_depth": [3, 5, 8, 10],
    "subsample": [0.8, 1],
}

GridSearchCV_GBC = GridSearchCV(estimator=GradientBoostingClassifier(),
                                param_grid=params_GBC,
                                cv=3,
                                scoring="accuracy",
                                return_train_score=True
                                )

# Fit model with train data
GridSearchCV_GBC.fit(X_train, Y_train);

print(f"Best estimator values for GBC model:\n{GridSearchCV_GBC.best_estimator_}")
print(f"Best parameter values for GBC model:\n{GridSearchCV_GBC.best_params_}")
print(f"Best score value foe GBC model: {round(GridSearchCV_GBC.best_score_, 3)}")

# Test with new parameter
gbc = GradientBoostingClassifier(learning_rate=0.5, loss="log_loss", max_depth=10, n_estimators=100, subsample=1,random_state=42)
gbc_mod = gbc.fit(X_train, Y_train)
pred_gbc = gbc_mod.predict(X_test)

mse_gbc = mean_squared_error(Y_test, pred_gbc)
rmse_gbc = np.sqrt(mean_squared_error(Y_test, pred_gbc))
score_gbc_train = gbc_mod.score(X_train, Y_train)
score_gbc_test = gbc_mod.score(X_test, Y_test)

print(f"Mean Square Error for Gradient Boosting Classifier = {round(mse_gbc, 3)}")
print(f"Root Mean Square Error for Gradient Boosting Classifier = {round(rmse_gbc, 3)}")
print(f"R^2(coefficient of determination) on training set = {round(score_gbc_train, 3)}")
print(f"R^2(coefficient of determination) on testing set = {round(score_gbc_test, 3)}")

print("Classification Report")
print(classification_report(Y_test, pred_gbc))
print("Confusion Matrix:")
print(confusion_matrix(Y_test, pred_gbc))

ax= plt.subplot()
sns.heatmap(confusion_matrix(Y_test, pred_gbc), annot=True, ax = ax, cmap = "GnBu");

ax.set_xlabel("Predicted Risk Levels");
ax.set_ylabel("True Risk Levels");
ax.set_title("Confusion Matrix");
ax.xaxis.set_ticklabels(["Low", "Mid", "High"]);
ax.yaxis.set_ticklabels(["Low", "Mid", "High"]);

# Create a DataFrame to store model evaluation results
results = pd.DataFrame({
    "Model": ["Logistic Regression", "K-Nearest Neighbors", "Random Forest", "Gradient Boosting Classifier"],
    "Train Score": [
        # Calculate mean cross-validated accuracy for training set
        cross_val_score(logistic_regression_mod, X_train, Y_train, cv=3).mean(),
        cross_val_score(knn_mod, X_train, Y_train, cv=3).mean(),
        cross_val_score(random_forest_mod, X_train, Y_train, cv=3).mean(),
        cross_val_score(gbc_mod, X_train, Y_train, cv=3).mean(),
    ],
    "Test Score": [
        # Calculate accuracy on the test set
        logistic_regression_mod.score(X_test, Y_test),
        knn_mod.score(X_test, Y_test),
        random_forest_mod.score(X_test, Y_test),
        gbc_mod.score(X_test, Y_test),
    ]
})
# Additional Metrics (precision, recall, F1 score)
metrics = ["precision", "recall", "f1"]
for metric in metrics:
    results[f"{metric.capitalize()}"] = [
        precision_recall_fscore_support(Y_test, model.predict(X_test), average="weighted")[metrics.index(metric)]
        for model in [logistic_regression_mod, knn_mod, random_forest_mod, gbc_mod]
    ]

result_df = results.sort_values(by="Test Score", ascending=False)
result_df = result_df.set_index("Test Score")
result_df

import pickle

filename ='finalized_maternal_model.sav'
pickle.dump (gbc_mod, open(filename,'wb'))

#loading the saved model
loaded_model1 = pickle.load(open('finalized_maternal_model.sav','rb'))

