import pandas as pd
import os
import time

def assign_label(row):
    path = str(row["path"]).lower()
    attack = str(row.get("attack_type", "")).lower()

    # Labeling Logic based on Attack Types
    if attack in ["sqli", "phpinfo", "xss"]: return 1
    if "?" in path and any(x in path for x in ["'", "--", "union", "select"]): return 9
    if "=" in path and any(x in path for x in ["sleep", "ls", "cat", "/bin/"]): return 8
    if "=" in path and any(x in path for x in ["<script", "<>", "%3c"]): return 5
    if path in ["/", "/style.css"]: return 0
    return -1

def prepare():
    input_path = "PyLog/Csv/parsed/parsed.csv"
    output_path = "PyLog/Csv/labeled/labeled.csv"
    
    # --- SYNCHRONIZATION HANDSHAKE ---
    # Wait for the OS to finalize the file write from Phase 1
    retries = 0
    while (not os.path.exists(input_path) or os.path.getsize(input_path) == 0) and retries < 20:
        time.sleep(0.5)
        retries += 1

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        print("Error: Phase 1 output not found or empty.")
        return False

    try:
        df = pd.read_csv(input_path)
        df["label"] = df.apply(assign_label, axis=1)
        
        # Frequency Logic for DoS detection
        ip_counts = df["source_ip"].value_counts()
        df["freq_label"] = df["source_ip"].apply(lambda x: 3 if ip_counts.get(x,0) >= 100 else 0)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print("[+] Phase 2: Labeling complete.")
        return True
    except Exception as e:
        print(f"Phase 2 Error: {e}")
        return False