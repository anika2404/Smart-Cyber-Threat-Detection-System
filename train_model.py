import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Load dataset
data = pd.read_csv("data/UNSW_NB15_testing-set.csv")

# Handle missing values
data.fillna(0, inplace=True)

# Encode categorical columns
encoders = {}
for col in ['proto', 'service', 'state']:
    if col in data.columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col].astype(str))
        encoders[col] = le

# Save encoders
os.makedirs("backend", exist_ok=True)
joblib.dump(encoders, "backend/encoders.pkl")

# Features and labels
drop_cols = [col for col in ['label', 'attack_cat'] if col in data.columns]
X = data.drop(columns=drop_cols, errors='ignore')
y = data['label']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "backend/model.pkl")

print("Model and encoders saved successfully.")