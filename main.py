import cv2
import time
import winsound
import threading
from ultralytics import YOLO

from alert import send_alert
from utils import ensure_folders, get_image_path, log_event


USE_PHONE_CAMERA = True
PHONE_CAMERA_URL = "http://10.250.179.201:8080/video"
LAPTOP_CAMERA_INDEX = 0

MODEL_PATH = "yolov8n.pt"

DANGER_OBJECTS = ["knife", "scissors"]

CONFIDENCE = 0.25
COOLDOWN = 8
FRAME_SKIP = 1


def setup_camera(cap):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def open_camera():
    if USE_PHONE_CAMERA:
        print("Trying phone camera...")
        cap = cv2.VideoCapture(PHONE_CAMERA_URL)
        setup_camera(cap)
        time.sleep(1)

        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print("Phone camera connected")
                return cap

        print("Phone camera failed. Switching to laptop camera...")
        cap.release()

    print("Trying laptop camera...")
    cap = cv2.VideoCapture(LAPTOP_CAMERA_INDEX, cv2.CAP_DSHOW)
    setup_camera(cap)
    time.sleep(1)

    if cap.isOpened():
        ret, _ = cap.read()
        if ret:
            print("Laptop camera connected")
            return cap

    print("No camera working!")
    return cap


def play_alarm():
    def sound():
        try:
            print("ALARM STARTED")

            # Loud beep alarm
            for _ in range(15):
                winsound.Beep(2500, 300)
                time.sleep(0.1)

        except Exception as e:
            print("Beep failed, using Windows default alarm:", e)

            try:
                for _ in range(10):
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                    time.sleep(0.4)
            except Exception as e2:
                print("Alarm completely failed:", e2)

    threading.Thread(target=sound, daemon=True).start()



def main():
    ensure_folders()

    print("Loading YOLO model...")
    model = YOLO(MODEL_PATH)

    cap = open_camera()

    if not cap.isOpened():
        print("Camera not working")
        return

    last_alert = 0
    frame_count = 0
    last_results = []

    print("SYSTEM STARTED")
    print("Press Q to quit")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Camera error. Reconnecting...")
            cap.release()
            time.sleep(1)
            cap = open_camera()
            continue

        original = frame.copy()
        frame_count += 1

        if frame_count % FRAME_SKIP == 0:
            try:
                last_results = model.predict(
                    frame,
                    imgsz=320,
                    conf=CONFIDENCE,
                    verbose=False
                )
            except Exception as e:
                print("Detection error:", e)
                continue

        detected = False
        best_label = ""
        best_conf = 0.0
        best_box = None

        for r in last_results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]

                if label not in DANGER_OBJECTS:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                if conf > best_conf:
                    detected = True
                    best_label = label
                    best_conf = conf
                    best_box = (x1, y1, x2, y2)

     
        if detected and best_box:
            x1, y1, x2, y2 = best_box

            cv2.rectangle(original, (x1, y1), (x2, y2), (0, 0, 255), 3)

            cv2.putText(
                original,
                f"{best_label.upper()} {best_conf:.2f}",
                (x1, max(35, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

            cv2.rectangle(original, (10, 10), (380, 65), (0, 0, 255), -1)
            cv2.putText(
                original,
                "THREAT DETECTED",
                (20, 47),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

        else:
            cv2.rectangle(original, (10, 10), (270, 65), (0, 180, 0), -1)
            cv2.putText(
                original,
                "MONITORING",
                (20, 47),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )


        if detected and time.time() - last_alert > COOLDOWN:
            print("WEAPON DETECTED:", best_label)

            image_path = get_image_path("weapon")
            cv2.imwrite(image_path, original)

            # Alarm sound
            play_alarm()

            # Telegram alert
            alert_status = send_alert(image_path, best_label, best_conf)

            if alert_status:
                log_event(best_label, best_conf, image_path, "sent")
            else:
                log_event(best_label, best_conf, image_path, "failed")

            last_alert = time.time()


        display = cv2.resize(original, (1000, 700))
        cv2.imshow("Weapon Detection System", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()