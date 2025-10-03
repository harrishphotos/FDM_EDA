#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score, roc_auc_score
import joblib


DATA_PATH = "NYC_YELLOW_TAXI_CLEAN.csv"
MODEL_DIR = "streamlit_app/models"
os.makedirs('streamlit_app/models', exist_ok=True)


# In[20]:



try:
    df = pd.read_csv("NYC_YELLOW_TAXI_CLEAN.csv")
    df.head()
    df.info()
    df.describe()
except FileNotFoundError:
    print("Error: CSV file not found. please check the file name.")
    exit()


# In[4]:


df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour


# In[5]:


features = ["trip_distance", "passenger_count", "trip_duration_min", "pickup_hour"]
y_fare = df["fare_amount"]
y_tip = (df["tip_amount"] > 2).astype(int)


# In[6]:


df_clean = df.dropna(subset=features + ["fare_amount", "tip_amount"])
X = df_clean[features]
y_fare = df_clean["fare_amount"]
if 'tip_amount' in df.columns:
    y_tip = (df_clean["tip_amount"] > 2).astype(int)
else:
    print("Warning: tip_amount column not found")

# In[7]:


from sklearn.model_selection import train_test_split

X_train, X_test, y_train_fare, y_test_fare = train_test_split(X, y_fare, test_size=0.2, random_state=42)
X_train2, X_test2, y_train_tip, y_test_tip = train_test_split(X, y_tip, test_size=0.2, random_state=42)


# In[8]:

print("\n Training models..")
lr = LinearRegression().fit(X_train, y_train_fare)
rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train_fare)


# In[9]:


clf = LogisticRegression(max_iter=1000).fit(X_train2, y_train_tip)
rf_clf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train2, y_train_tip)


# In[10]:


y_pred_lr = lr.predict(X_test)
rmse_lr = np.sqrt(mean_squared_error(y_test_fare, y_pred_lr))
r2_lr = r2_score(y_test_fare, y_pred_lr)


# In[11]:


y_pred_rf = rf.predict(X_test)
rmse_rf = np.sqrt(mean_squared_error(y_test_fare, y_pred_rf))
r2_rf = r2_score(y_test_fare, y_pred_rf)


# In[12]:


y_pred_clf = clf.predict(X_test2)
acc_clf = accuracy_score(y_test_tip, y_pred_clf)
f1_clf = f1_score(y_test_tip, y_pred_clf)


# In[13]:


y_pred_rf2 = rf_clf.predict(X_test2)
acc_rf = accuracy_score(y_test_tip, y_pred_rf2)
f1_rf = f1_score(y_test_tip, y_pred_rf2)


# In[14]:

print("\n Model Performance:")
print("Linear Regression RMSE:", rmse_lr, " R2:", r2_lr)
print("Random Forest RMSE:", rmse_rf, " R2:", r2_rf)
print("Logistic Regression Accuracy:", acc_clf, " F1:", f1_clf)
print("Random Forest Accuracy:", acc_rf, " F1:", f1_rf)


# In[16]:


from sklearn.model_selection import GridSearchCV


# In[17]:


param_grid = {"n_estimators": [100, 200], "max_depth": [5, 10, None]}
grid = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=3, scoring="neg_mean_squared_error")
grid.fit(X_train, y_train_fare)


# In[18]:


param_grid_clf = {"n_estimators": [100, 200], "max_depth": [5, 10, None]}
grid_clf = GridSearchCV(RandomForestClassifier(random_state=42), param_grid_clf, cv=3, scoring="f1")
grid_clf.fit(X_train2, y_train_tip)


# In[19]:


print("Best Params (Fare):", grid.best_params_)
print("Best Score (Fare RMSE):", (-grid.best_score_)**0.5)
print("Best Params (Tip):", grid_clf.best_params_)
print("Best Score (Tip F1):", grid_clf.best_score_)


# In[26]:


import matplotlib.pyplot as plt
import seaborn as sns


# In[27]:


importances = rf.feature_importances_
indices = importances.argsort()[::-1]
sorted_features = [features[i] for i in indices]
sorted_importances = importances[indices]


# In[28]:


plt.figure(figsize=(8,5))
sns.barplot(x=sorted_importances, y=sorted_features)
plt.title("Feature Importance - Fare Prediction")
plt.savefig('feature_importance.png')
plt.show()


# In[29]:


plt.figure(figsize=(6,4))
sns.scatterplot(x=y_test_fare, y=y_pred_rf, alpha=0.5)
plt.xlabel("Actual Fare")
plt.ylabel("Predicted Fare")
plt.title("Random Forest - Actual vs Predicted Fares")
plt.savefig('actual_vs_predicted.png')
plt.show()


# In[30]:


from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
cm = confusion_matrix(y_test_tip, y_pred_rf2)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Tip", "Tip"])
disp.plot(cmap="Blues")
plt.title("Tip Classification - Confusion Matrix")
plt.savefig('confusion_matrix.png')
plt.show()


# In[ ]:
joblib.dump(rf, 'streamlit_app/models/fare_model.pkl')
joblib.dump(rf_clf, 'streamlit_app/models/tip_model.pkl')
print("✅ Models saved successfully!")



