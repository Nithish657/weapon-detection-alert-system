import requests
from datetime import datetime

BOT_TOKEN = "8601672780:AAFGGO2NWLgFGJQSkA5V338huF-oEwkBQ3w"
CHAT_ID = "8534758416"


def send_alert(image_path, label, conf):
    try:
        text = (
            f"🚨 SECURITY ALERT\n"
            f"Threat: {label}\n"
            f"Confidence: {conf:.2f}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        msg_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )

        with open(image_path, "rb") as img:
            photo_response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID},
                files={"photo": img},
                timeout=20
            )

        if msg_response.status_code == 200 and photo_response.status_code == 200:
            print("Telegram alert sent")
            return True
        else:
            print("Telegram error:", msg_response.text, photo_response.text)
            return False

    except Exception as e:
        print("Alert error:", e)
        return False