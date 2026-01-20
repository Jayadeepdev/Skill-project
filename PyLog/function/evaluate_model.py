import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

INPUT_FILE = "data/output/final_output.csv"
REPORT_FILE = "data/output/evaluation_summary.csv"

ATTACK_LABELS = [5, 8, 9]   # XSS, CMDi, SQLi


def calculate_risk(row):
    score = 0

    # Semantic attack
    if row["predicted_label"] in ATTACK_LABELS:
        score += 5

    # Behavioral anomaly
    if row["behavior_anomaly"] == -1:
        score += 3

    # Aggressive source
    if row["freq_label"] >= 2:
        score += 2

    return score


def main():
    print("======== Loading Output CSV ========")
    df = pd.read_csv(INPUT_FILE)

    # ------------------------------------------------
    # 1. Filter rows with known ground truth
    # ------------------------------------------------
    df_known = df[df["label"] != -1]

    print(f"[+] Known-label rows: {len(df_known)}")
    print(f"[+] Unlabeled rows: {len(df) - len(df_known)}")

    # ------------------------------------------------
    # 2. Basic accuracy (sanity check)
    # ------------------------------------------------
    accuracy = accuracy_score(
        df_known["label"],
        df_known["predicted_label"]
    )

    print("\n======== Basic Accuracy ========")
    print("Accuracy:", round(accuracy, 4))

    # ------------------------------------------------
    # 3. Classification report
    # ------------------------------------------------
    print("\n======== Classification Report ========")
    print(
        classification_report(
            df_known["label"],
            df_known["predicted_label"],
            zero_division=0
        )
    )

    # ------------------------------------------------
    # 4. Confusion Matrix
    # ------------------------------------------------
    print("\n======== Confusion Matrix ========")
    cm = confusion_matrix(
        df_known["label"],
        df_known["predicted_label"],
        labels=[0, 5, 8, 9]
    )

    cm_df = pd.DataFrame(
        cm,
        index=["true_0", "true_5", "true_8", "true_9"],
        columns=["pred_0", "pred_5", "pred_8", "pred_9"]
    )

    print(cm_df)

    # ------------------------------------------------
    # 5. Attack recall (MODEL QUALITY, NOT ALERTING)
    # ------------------------------------------------
    df_attacks = df_known[df_known["label"].isin(ATTACK_LABELS)]

    attack_recall = (
        df_attacks["predicted_label"].isin(ATTACK_LABELS)
    ).mean()

    print("\n======== Attack Recall ========")
    print("Attack recall:", round(attack_recall, 4))

    # ------------------------------------------------
    # 6. Risk scoring + threat type
    # ------------------------------------------------
    df["risk_score"] = df.apply(calculate_risk, axis=1)

    df["threat_type"] = "normal"
    df.loc[df["behavior_anomaly"] == -1, "threat_type"] = "recon"
    df.loc[df["predicted_label"].isin(ATTACK_LABELS), "threat_type"] = "attack"

    # ------------------------------------------------
    # 7. Alert level (SOC-style tiers)
    # ------------------------------------------------
    df["alert_level"] = "none"
    df.loc[df["risk_score"] >= 7, "alert_level"] = "high"
    df.loc[
        (df["risk_score"] >= 5) & (df["risk_score"] < 7),
        "alert_level"
    ] = "medium"

    # ------------------------------------------------
    # 8. ML discovery on previously unlabeled data
    # ------------------------------------------------
    df_unknown = df[df["label"] == -1].copy()
    df_unknown["ml_attack"] = df_unknown["predicted_label"].isin(ATTACK_LABELS)

    discovery_rate = df_unknown["ml_attack"].mean()

    print("\n======== Discovery on Unlabeled Data ========")
    print("ML flagged attacks:", round(discovery_rate * 100, 2), "%")

    # ------------------------------------------------
    # 9. High-confidence alerts
    # ------------------------------------------------
    high_confidence = df[df["alert_level"] == "high"]

    print("\n======== High-Confidence Alerts ========")
    print("Count:", len(high_confidence))

    # ------------------------------------------------
    # 10. Save evaluation summary
    # ------------------------------------------------
    summary = {
        "total_rows": len(df),
        "known_rows": len(df_known),
        "unlabeled_rows": len(df_unknown),
        "accuracy": accuracy,
        "attack_recall": attack_recall,
        "unlabeled_attack_rate": discovery_rate,
        "high_confidence_alerts": len(high_confidence)
    }

    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(REPORT_FILE, index=False)

    print("\n[+] Evaluation summary saved to:", REPORT_FILE)


if __name__ == "__main__":
    main()
