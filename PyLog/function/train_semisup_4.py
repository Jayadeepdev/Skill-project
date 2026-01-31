import pandas as pd
from sklearn.semi_supervised import LabelSpreading
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import joblib
import os
import time

def train():
    input_path = "PyLog/Csv/features_semisup/features_semisup.csv"
    model_dir = "PyLog/Model"
    
    # --- SYNCHRONIZATION HANDSHAKE ---
    # Ensure Phase 3 has finished writing the features file
    retry = 0
    while (not os.path.exists(input_path) or os.path.getsize(input_path) == 0) and retry < 20:
        time.sleep(0.5)
        retry += 1

    if not os.path.exists(input_path):
        print(f"[-] Error: {input_path} not found.")
        return False

    try:
        df = pd.read_csv(input_path)
        df_clean = df.fillna(0)

        # Ensure we don't try to sample more than we have
        TRAIN_SIZE = min(25000, len(df_clean))
        df_train = resample(df_clean, n_samples=TRAIN_SIZE, random_state=500)

        X_train_df = df_train.drop(columns=["label"], errors='ignore')
        y_train = df_train["label"]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_df)

        # FIX: LabelSpreading is naturally multiclass-safe
        model = LabelSpreading(kernel="rbf", gamma=15, max_iter=300)
        model.fit(X_train_scaled, y_train)

        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(model, os.path.join(model_dir, "semisup_model.joblib"))
        joblib.dump(scaler, os.path.join(model_dir, "semisup_scaler.joblib"))

        print("[+] Training Phase 4 Successful.")
        return True
    except Exception as e:
        print(f"[-] Training Error: {str(e)}")
        return False