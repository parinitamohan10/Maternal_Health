# -*- coding: utf-8 -*-
"""Fetal_Health_Classifier

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18MzP4raIK1TiIa_Jt0FTSNrTrILRaPsK
"""

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

"""FETAL HEALTH CLASSIFICATION"""

df2 = pd.read_csv('/content/fetal_health.csv')
df2.head()

df2.info()

sns.pairplot(df2, hue='fetal_health')

columns = ['baseline value', 'accelerations', 'fetal_movement',
       'uterine_contractions', 'light_decelerations', 'severe_decelerations',
       'prolongued_decelerations', 'abnormal_short_term_variability',
       'mean_value_of_short_term_variability',
       'percentage_of_time_with_abnormal_long_term_variability',
       'mean_value_of_long_term_variability', 'histogram_width',
       'histogram_min', 'histogram_max', 'histogram_number_of_peaks',
       'histogram_number_of_zeroes', 'histogram_mode', 'histogram_mean',
       'histogram_median', 'histogram_variance', 'histogram_tendency']
scale_X = StandardScaler()
X =  pd.DataFrame(scale_X.fit_transform(df2.drop(["fetal_health"],axis = 1),), columns = columns)

X.head()

y = df2["fetal_health"]

# Importing train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 42, stratify = y)

X_train.shape, X_test.shape, y_train.shape, y_test.shape

from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score

"""Gradient Boost Classifier"""

# Initialize and train the Gradient Boosting Classifier model
gb_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)  # You can adjust the number of estimators
gb_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = gb_classifier.predict(X_test)

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')  # Weighted precision for multiclass
recall = recall_score(y_test, y_pred, average='weighted')  # Weighted recall for multiclass
f1 = f1_score(y_test, y_pred, average='weighted')  # Weighted F1 score for multiclass

# Calculate AUC for multiclass
y_scores = gb_classifier.predict_proba(X_test)
auc = roc_auc_score(y_test, y_scores, average='weighted', multi_class='ovr')

# Calculate specificity for the entire multiclass problem
confusion = confusion_matrix(y_test, y_pred)
true_negatives = np.sum(np.diag(confusion))
false_positives = np.sum(confusion) - true_negatives
specificity = true_negatives / (true_negatives + false_positives)

# Print the evaluation metrics, AUC, and specificity
print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1:.2f}")
print(f"AUC: {auc:.2f}")
print(f"Specificity: {specificity:.2f}")

import pickle

filename ='fetal_health_classifier.sav'
pickle.dump (gb_classifier, open('fetal_health_classifier.sav','wb'))

#loading the saving model
loaded_model = pickle.load(open('fetal_health_classifier.sav','rb'))