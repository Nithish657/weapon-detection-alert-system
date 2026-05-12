import cv2, subprocess, sys

cap = cv2.VideoCapture("http://10.250.179.201:8080/video")

ret,f1 = cap.read()
ret,f2 = cap.read()

while True:
    diff = cv2.absdiff(f1,f2)
    if diff.mean() > 10:
        print("Motion Detected")
        subprocess.Popen([sys.executable,"main.py"])
        break

    f1 = f2
    ret,f2 = cap.read()

cap.release()