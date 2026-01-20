import pandas as pd
from sklearn.semi_supervised import LabelSpreading
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import joblib


# Load features 
df = pd.read_csv("PyLog/Csv/features_semisup/features_semisup.csv")

def train():
    #  CLEAN DATA
    df_clean = df.fillna(0)

    #  SUBSAMPLE
    TRAIN_SIZE = 25000

    df_train = resample(
        df_clean,
        n_samples=TRAIN_SIZE,
        random_state=500
    )

    #  SPLIT FEATURES / LABELS (SAFE)

    X_train_df = df_train.drop(columns=["label"])
    y_train = df_train["label"]

    #  SCALE FEATURES (DO NOT OVERWRITE df)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_df)

    # TRAIN SEMI-SUPERVISED MODEL
    model = LabelSpreading(
        kernel="rbf",
        gamma=15,
        max_iter=300
    )

    model.fit(X_train_scaled, y_train)

    #SAVE MODEL + SCALER
    
    joblib.dump(model, "PyLog/Model/semisup_model.joblib")
    joblib.dump(scaler, "PyLog/Model/semisup_scaler.joblib")

    print("[+] Semi-supervised model trained successfully")
    return True

if __name__ == "__main__":
    train()
