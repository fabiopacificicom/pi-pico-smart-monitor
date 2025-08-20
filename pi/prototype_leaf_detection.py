"""
Prototype: Leaf Detection and Cropping with YOLOv5 Nano (pre-trained)

- Loads a YOLOv5 Nano model (Torch Hub or local .pt file)
- Runs detection on all images in test_images/
- Crops detected leaves and saves them to leaf_crops/
- Designed for prototyping and dataset building

Requirements:
- torch
- torchvision
- opencv-python
- (Download YOLOv5 Nano weights if not using Torch Hub)
"""

import os
import cv2
import torch
from pathlib import Path

# Paths
TEST_IMAGES_DIR = Path(__file__).parent / 'test_images'
CROPS_DIR = Path(__file__).parent / 'leaf_crops'
CROPS_DIR.mkdir(exist_ok=True)

# Load YOLOv5 Nano model from Torch Hub (internet required for first run)
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
model.conf = 0.3  # confidence threshold

# Supported image extensions
IMG_EXTS = ['.jpg', '.jpeg', '.png']

for img_path in TEST_IMAGES_DIR.iterdir():
    if img_path.suffix.lower() not in IMG_EXTS:
        continue
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Failed to load {img_path}")
        continue
    # Run detection
    results = model(img)
    # results.xyxy[0]: [x1, y1, x2, y2, conf, cls]
    for i, det in enumerate(results.xyxy[0]):
        x1, y1, x2, y2, conf, cls = det.tolist()
        # Optionally, filter for 'plant' or 'leaf' class if available
        crop = img[int(y1):int(y2), int(x1):int(x2)]
        crop_name = f"{img_path.stem}_crop_{i}.jpg"
        crop_path = CROPS_DIR / crop_name
        cv2.imwrite(str(crop_path), crop)
        print(f"Saved crop: {crop_path}")
print("Done. Check leaf_crops/ for results.")
