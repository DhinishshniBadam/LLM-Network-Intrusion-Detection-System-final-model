import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

cat_cols = ['protocol_type', 'service', 'flag']

# structural features derived from raw traffic fields
STRUCTURAL_COLS = [
    'duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent',
    'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
    'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login',
    'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
    'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
    'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
]

def get_encoders(path):
    df = pd.read_csv(path)
    encoders = {}
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            le.fit(df[col])
            encoders[col] = le
    return encoders

def to_payload_text(row):
    """Convert categorical fields into a text string for BERT tokenization."""
    return f"protocol {row['protocol_type']} service {row['service']} flag {row['flag']}"

def to_web_payload_text(url: str, payload: str, headers: dict, net: dict) -> str:
    """Build enriched BERT input text from web request + network features."""
    ua = headers.get("User-Agent", "") if headers else ""
    ct = headers.get("Content-Type", "") if headers else ""
    proto = net.get("protocol_type", "")
    service = net.get("service", "")
    flag = net.get("flag", "")
    return f"url {url} payload {payload} agent {ua} content {ct} protocol {proto} service {service} flag {flag}"

def extract_structural(df, scaler=None, fit_scaler=False):
    """Extract and scale structural (numeric) features."""
    cols = [c for c in STRUCTURAL_COLS if c in df.columns]
    X_struct = df[cols].values.astype(np.float32)
    if fit_scaler:
        scaler = StandardScaler()
        X_struct = scaler.fit_transform(X_struct)
        return X_struct, scaler
    elif scaler:
        X_struct = scaler.transform(X_struct)
    return X_struct, scaler

def load_data(path, encoders=None):
    df = pd.read_csv(path)
    for col in cat_cols:
        if col in df.columns:
            if encoders:
                df[col] = encoders[col].transform(df[col])
            else:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
    if "class" in df.columns:
        y = (df["class"] == "anomaly").astype(int).values
        df = df.drop("class", axis=1)
    else:
        y = None
    return df, y
