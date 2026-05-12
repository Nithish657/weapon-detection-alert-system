import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Weapon Detection Demo",
    layout="centered"
)

st.title("Weapon Detection and Alert System")
st.write("Upload an image to detect weapons using YOLOv8.")

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

DANGER_OBJECTS = ["knife", "scissors"]

uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.subheader("Uploaded Image")
    st.image(image, use_container_width=True)

    img_array = np.array(image)

    results = model.predict(
        img_array,
        imgsz=320,
        conf=0.25,
        verbose=False
    )

    detected = False

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])

            if label in DANGER_OBJECTS:
                detected = True
                st.error(f"⚠️ THREAT DETECTED: {label.upper()} ({conf:.2f})")

    output_img = results[0].plot()

    st.subheader("Detection Output")
    st.image(output_img, use_container_width=True)

    if not detected:
        st.success("✅ No weapon detected")
else:
    st.info("Please upload an image to start detection.")
