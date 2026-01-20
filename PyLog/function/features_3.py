import pandas as pd
from sklearn.preprocessing import LabelEncoder



def features():
    df = pd.read_csv("PyLog/Csv/labeled/labeled.csv")

    # Encode HTTP method
    le = LabelEncoder()
    df["method_enc"] = le.fit_transform(df["http_method"].fillna("NONE"))

    df["path_len"] = df["path"].fillna("").apply(len)
    df["path_depth"] = df["path"].fillna("").str.count("/")
    df["has_query"] = df["path"].fillna("").str.contains(r"\?|%27|--", regex=True).astype(int)
    df["has_values"] = df["path"].fillna("").str.contains("=").astype(int)
    df["is_php"] = df["path"].fillna("").str.contains(".php", regex=False).astype(int)
    df["is_static"] = df["path"].fillna("").str.contains(r"\.css|\.js|\.png|\.jpg", regex=True).astype(int)

    features = df[
        [
            "method_enc",
            "path_len",
            "path_depth",
            "has_query",
            "has_values",
            "is_php",
            "is_static",
            "label",
            "freq_label"
        ]
    ]

    features.to_csv("PyLog/Csv/features_semisup/features_semisup.csv", index=False)
    print("[+] features.csv created")
    return True
