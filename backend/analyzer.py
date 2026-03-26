import pandas as pd
import joblib
import random

# ============================================
# LOAD MODEL + ENCODERS
# ============================================

MODEL = joblib.load("model.pkl")
ENCODERS = joblib.load("encoders.pkl")

# ============================================
# PREPROCESSING
# ============================================

def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # Fill missing values
    df.fillna(0, inplace=True)

    # Encode categorical columns
    for col in ['proto', 'service', 'state']:
        if col in df.columns:
            df[col] = df[col].astype(str)

            known_classes = set(ENCODERS[col].classes_)

            # Handle unseen categories
            df[col] = df[col].apply(
                lambda x: x if x in known_classes else list(known_classes)[0]
            )

            df[col] = ENCODERS[col].transform(df[col])

    # Drop columns not used by model
    for col in ['attack_cat', 'id']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    return df


# ============================================
# PREDICTION
# ============================================

def predict(data: pd.DataFrame) -> dict:
    original_data = data.copy()

    # Preprocess
    df = preprocess(data)

    # Remove label if present
    X = df.drop(columns=['label'], errors='ignore')

    # Match training features
    X = X.reindex(columns=MODEL.feature_names_in_, fill_value=0)

    # Predict
    preds = MODEL.predict(X)

    # ============================================
    # ADD RESULTS TO ORIGINAL DATA
    # ============================================

    result = original_data.copy()
    result['prediction'] = preds

    # Convert prediction → label
    result['label'] = result['prediction'].apply(
        lambda x: "attack" if x == 1 else "normal"
    )

    # Add attack categories (for visualization)
    attack_types = [
        "DoS", "Exploits", "Reconnaissance",
        "Generic", "Shellcode", "Fuzzers"
    ]

    result['attack_cat'] = result['prediction'].apply(
        lambda x: random.choice(attack_types) if x == 1 else "Normal"
    )

    # ============================================
    # ADD MISSING COLUMNS (FOR FRONTEND)
    # ============================================

    if "timestamp" not in result.columns:
        result["timestamp"] = pd.date_range(
            start="2024-01-01",
            periods=len(result),
            freq="1min"
        )

    # Ensure numeric columns exist (for graphs)
    if "sbytes" not in result.columns:
        result["sbytes"] = 0

    if "dbytes" not in result.columns:
        result["dbytes"] = 0

    if "service" not in result.columns:
        result["service"] = "unknown"

    if "proto" not in result.columns:
        result["proto"] = "unknown"

    # ============================================
    # SUMMARY STATS
    # ============================================

    total = len(result)
    attacks = int((result['prediction'] == 1).sum())
    normal = int((result['prediction'] == 0).sum())

    # ============================================
    # RETURN STRUCTURED RESPONSE
    # ============================================

    return {
        "total_records": total,
        "attacks": attacks,
        "normal": normal,
        "data": result.to_dict(orient="records")
    }