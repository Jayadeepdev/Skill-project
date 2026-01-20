import re
import pandas as pd

log_files = "data/input/input.log"
# Regex patterns
request_pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+'
    r'\[(?P<date>\d{2}/\w{3}/\d{4}):'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+[+\-]\d{4}\]\s+'
    r'"(?P<method>GET|POST|PUT|HEAD|DELETE)\s+'
    r'(?P<path>\S+)\s+HTTP/\d\.\d"\s+'
    r'(?P<status>\d{3})\s+'
    r'(?P<size>\d+|-)',
    re.IGNORECASE
)

attack_pattern = re.compile(
    r'Glaspot:\s+(?P<attack>[\w_]+)\s+attack\s+method\s+from\s+'
    r'(?P<ip>\d+\.\d+\.\d+\.\d+)',
    re.IGNORECASE
)

rows = []

def parser(log_file=log_files):

    with open(log_file, "r", errors="ignore") as f:
        for line in f:
            req = request_pattern.search(line)
            atk = attack_pattern.search(line)

            if req:
                rows.append({
                    "date": req.group("date"),
                    "time": req.group("time"),
                    "source_ip": req.group("ip"),
                    "http_method": req.group("method"),
                    "path": req.group("path"),
                    "attack_type": "unknown",
                    "status_code":req.group("status"),
                    "raw_log": line.strip()
                })

            elif atk:
                rows.append({
                    "date": "",
                    "time": "",
                    "source_ip": atk.group("ip"),
                    "http_method": "",
                    "path": "",
                    "attack_type": atk.group("attack"),
                    "raw_log": line.strip()
                })

    df = pd.DataFrame(rows)
    df.to_csv("PyLog/Csv/parsed/parsed.csv", index=False)
    print("[+] parsed.csv created")
    return True
