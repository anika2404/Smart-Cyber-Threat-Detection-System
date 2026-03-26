import pandas as pd
import joblib

MODEL = joblib.load("model.pkl")
ENCODERS = joblib.load("encoders.pkl")


def preprocess(data):
    df = data.copy()
    df.fillna(0, inplace=True)

    for col in ['proto', 'service', 'state']:
        if col in df.columns:
            df[col] = df[col].astype(str)
            known = set(ENCODERS[col].classes_)
            fallback = list(known)[0]
            df[col] = df[col].apply(lambda x: x if x in known else fallback)
            df[col] = ENCODERS[col].transform(df[col])

    for col in ['attack_cat', 'id']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    return df


def predict(data):
    df = preprocess(data)

    X = df.drop(columns=['label'], errors='ignore')
    X = X.reindex(columns=MODEL.feature_names_in_, fill_value=0)

    preds = MODEL.predict(X)

    result = data.copy()
    result['prediction'] = preds

    return result