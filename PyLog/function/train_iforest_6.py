import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

def iforest():
    df = pd.read_csv("data/output/semisup_output.csv")
    behavior_features = df[
        [
            "path_len",
            "path_depth",
            "has_query",
            "has_values",
            "label",
            "predicted_label",
            "is_static",
            "freq_label"
        ]
    ]

    model = IsolationForest(
        n_estimators=8000,
        contamination=0.5,
        random_state=300
    )

    df["behavior_anomaly"] = model.fit_predict(behavior_features)

    joblib.dump(model, "PyLog/Model/iforest_model.joblib")

    df.to_csv("data/output/final_output.csv", index=False)
    print("[+] Final output generated")
    return True


if __name__ == "__main__":
    iforest()