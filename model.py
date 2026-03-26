import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import requests 
import io

import os
print(os.listdir())
print(os.listdir("data"))
# Load dataset
data = pd.read_csv("data/UNSW_NB15_testing-set.csv")

# Handle missing values
data.fillna(0, inplace=True)
# Encode categorical columns
encoders = {}
for col in ['proto', 'service', 'state']:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col].astype(str))
    encoders[col] = le

# Save encoders (IMPORTANT)
joblib.dump(encoders, "backend/encoders.pkl")

# Features & labels
X = data.drop(['label', 'attack_cat'], axis=1)
y = data['label']

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Save model
joblib.dump(model, "backend/model.pkl")

print("✅ Model and encoders saved successfully")