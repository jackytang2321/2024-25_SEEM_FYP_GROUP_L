import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.inspection import permutation_importance
from sklearn import preprocessing

filename = "data_rating_test.csv"
data=pd.read_csv(filename)

x_data = data.drop(["result"], axis=1)
y_data = data["result"]
scaler = preprocessing.MinMaxScaler(feature_range=(0, 1)).fit(x_data)
x_data_scaled = scaler.transform(x_data)
x_train, x_test, y_train, y_test = train_test_split(x_data_scaled, y_data, random_state=21)

lr = LogisticRegression()
lr.fit(x_train, y_train)

model_fi = permutation_importance(lr, x_data_scaled, y_data, random_state=21)
data_importances = model_fi.importances_mean
print("Data Importances", data_importances)

print("Model Coefficients", lr.coef_)
# print("Model Intercepts", lr.intercept_)

lr.predict(x_test)
y_predict = lr.predict(x_test)
accuracy = accuracy_score(y_test, y_predict)

print("Model Accuracy", accuracy)