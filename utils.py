import os
import csv
from datetime import datetime


def ensure_folders():
    os.makedirs("evidence", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def get_image_path(label):
    filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    return os.path.join("evidence", filename)


def log_event(label, conf, img, status):
    log_path = os.path.join("logs", "log.csv")

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Time", "Label", "Confidence", "Image Path", "Status"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            label,
            f"{conf:.2f}",
            img,
            status
        ])