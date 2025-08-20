
"""
Prototype: On-Demand Leaf Detection and Cropping with YOLOv5 Nano (pre-trained)

- Captures a frame from the Pi webcam using OpenCV
- Runs YOLOv5 Nano detection on the captured frame
- Crops detected leaves and saves them to leaf_crops/
- Exposes a Flask endpoint to trigger the process remotely

Requirements:
- torch
- torchvision
- opencv-python
- flask
"""

import os
import cv2
import torch
from pathlib import Path
from flask import Flask, jsonify

# Paths
CROPS_DIR = Path(__file__).parent / 'leaf_crops'
CROPS_DIR.mkdir(exist_ok=True)

# Load YOLOv5 Nano model from Torch Hub (internet required for first run)
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
model.conf = 0.3  # confidence threshold

def capture_and_detect_and_crop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Failed to capture frame from webcam.")
    results = model(frame)
    crops = []
    dets = results.xyxy[0]
    if len(dets) == 0:
        # No detections: save the whole frame as a fallback crop
        crop_name = "capture_crop_full.jpg"
        crop_path = CROPS_DIR / crop_name
        cv2.imwrite(str(crop_path), frame)
        crops.append(str(crop_path))
    else:
        for i, det in enumerate(dets):
            x1, y1, x2, y2, conf, cls = det.tolist()
            crop = frame[int(y1):int(y2), int(x1):int(x2)]
            crop_name = f"capture_crop_{i}.jpg"
            crop_path = CROPS_DIR / crop_name
            cv2.imwrite(str(crop_path), crop)
            crops.append(str(crop_path))
    return crops

# Flask app for on-demand capture and detection
app = Flask(__name__)

@app.route('/plant_health/capture_and_detect', methods=['POST', 'GET'])
def plant_health_capture_and_detect():
    try:
        crops = capture_and_detect_and_crop()
        return jsonify({"status": "ok", "num_crops": len(crops), "crops": crops})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)
