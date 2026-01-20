import pandas as pd
import joblib

# Load data, model, scaler
def predict():
    df = pd.read_csv("PyLog/Csv/features_semisup/features_semisup.csv")

    model = joblib.load("PyLog/Model/semisup_model.joblib")
    scaler = joblib.load("PyLog/Model/semisup_scaler.joblib")

    
    # Prepare feature matrix
    
    FEATURES = [
        "method_enc",
        "path_len",
        "path_depth",
        "has_query",
        "has_values",
        "is_php",
        "is_static",
        "label"
    ]

    X_df = df[FEATURES].fillna(0)

    # Convert to NumPy + scale (match training)
    X_all = scaler.transform(X_df.values)

    
    # BATCHED PREDICTION (CRITICAL FIX)
    
    BATCH_SIZE = 6000   # safe on most machines
    predictions = []

    for i in range(0, len(X_all), BATCH_SIZE):
        batch = X_all[i:i + BATCH_SIZE]
        preds = model.predict(batch)
        predictions.extend(preds)

    df["predicted_label"] = predictions

    df.to_csv("data/output/semisup_output.csv", index=False)
    print("[+] Semi-supervised prediction complete (batched)")
    return True



if __name__ == "__main__":
    predict()