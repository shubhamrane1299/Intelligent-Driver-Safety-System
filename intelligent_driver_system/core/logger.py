import csv
import time
import os

def log_state(state):
    file_exists = os.path.isfile("logs.csv")

    with open("logs.csv", "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Timestamp", "State"])

        writer.writerow([time.strftime("%H:%M:%S"), state])