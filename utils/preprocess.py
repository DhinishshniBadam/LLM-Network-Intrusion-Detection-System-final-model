import pandas as pd
from sklearn.preprocessing import LabelEncoder

def get_encoders(path):
    df = pd.read_csv(path)
    cat_cols = ['protocol_type','service','flag']
    encoders = {}
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            le.fit(df[col])
            encoders[col] = le
    return encoders

def load_data(path):

    df = pd.read_csv(path)

    # categorical columns
    cat_cols = ['protocol_type','service','flag']

    # encode categorical columns
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])

    # if training file
    if "class" in df.columns:
        X = df.drop("class",axis=1)
        y = df["class"]
        return X,y

    # if test file
    else:
        return df,None