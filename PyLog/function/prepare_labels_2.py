import pandas as pd

df = pd.read_csv("PyLog/Csv/parsed/parsed.csv")

ip_counts = df["source_ip"].value_counts()

def assign_label(row):
    path = str(row["path"]).lower()
    attack = str(row["attack_type"]).lower()

    if attack in ["sqli", "phpinfo", "xss"]:
        return 1

    if "?" in path and any(x in path for x in [
        "'", "%27", "--", "union", "select",
        " or ", "%20or%20", " and ", "%20and%20"
    ]):
        return 9  #sqli attack

    if "=" in path and any(x in path for x in [
        "sleep", "%28", "%29", "ls", "cat", "echo", "/bin/"
    ]):
        return 8 #command injuction

    if "=" in path and any(x in path for x in [
        "<script", "%3cscript", "<>", "<></>"
    ]):
        return 5 #xss

    if path in ["/", "/style.css", "/robots.txt", "/favicon.ico"]:
        return 0 #normal

    return -1  #somting abnormal


def freq_score(ip):
    count = ip_counts.get(ip, 0)
    if count >= 100:
        return 3
    elif count >= 30:
        return 2
    elif count >= 10:
        return 1
    else:
        return 0
def prepare(func=assign_label):
    df["label"] = df.apply(func, axis=1)


    df["freq_label"] = df["source_ip"].apply(freq_score)

    df.to_csv("PyLog/Csv/labeled/labeled.csv", index=False)

    print("Label counts:")
    print(df["label"].value_counts())

    print("\nFrequency label counts:")
    print(df["freq_label"].value_counts())
    return True

if __name__ == "__main__":
    prepare()
