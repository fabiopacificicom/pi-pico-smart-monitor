
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
from flask import Blueprint, jsonify, send_from_directory

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
    names = model.names if hasattr(model, 'names') else {}
    print(f"Detections: {len(dets)}")
    for i, det in enumerate(dets):
        x1, y1, x2, y2, conf, cls = det.tolist()
        label = names.get(int(cls), str(cls))
        print(f"Detection {i}: class={label}, conf={conf:.2f}, box=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})")
        if conf >= model.conf:
            crop = frame[int(y1):int(y2), int(x1):int(x2)]
            crop_name = f"capture_crop_{i}_{label}.jpg"
            crop_path = CROPS_DIR / crop_name
            cv2.imwrite(str(crop_path), crop)
            crops.append(crop_name)
    if not crops:
        print("No objects detected above confidence threshold. Splitting full frame into grid crops.")
        # Split the frame into a grid (e.g., 4x4)
        grid_rows, grid_cols = 4, 4
        h, w, _ = frame.shape
        crop_h, crop_w = h // grid_rows, w // grid_cols
        crop_count = 0
        for row in range(grid_rows):
            for col in range(grid_cols):
                y1 = row * crop_h
                y2 = (row + 1) * crop_h if row < grid_rows - 1 else h
                x1 = col * crop_w
                x2 = (col + 1) * crop_w if col < grid_cols - 1 else w
                crop = frame[y1:y2, x1:x2]
                crop_name = f"capture_crop_grid_{row}_{col}.jpg"
                crop_path = CROPS_DIR / crop_name
                cv2.imwrite(str(crop_path), crop)
                crops.append(crop_name)
                crop_count += 1
        print(f"Saved {crop_count} grid crops.")
    return crops


# Flask Blueprint for plant health check
plant_health_api = Blueprint('plant_health_api', __name__)

@plant_health_api.route('/crops/<path:filename>')
def serve_crop(filename):
    return send_from_directory(str(CROPS_DIR), filename)

@plant_health_api.route('/plant_health/capture_and_detect', methods=['POST', 'GET'])
def plant_health_capture_and_detect():
    try:
        crops = capture_and_detect_and_crop()
        crop_urls = [f"/crops/{name}" for name in crops]
        return jsonify({"status": "ok", "num_crops": len(crop_urls), "crops": crop_urls})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
