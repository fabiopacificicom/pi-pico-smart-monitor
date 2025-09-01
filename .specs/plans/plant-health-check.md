
# Plant Health Check Feature Spec

## Overview

This document details the confirmed approach for implementing a plant health check feature on the Raspberry Pi using computer vision and machine learning. The system will detect plant leaves in images, crop them, and (optionally) classify their health status. The pipeline is modular, supporting dataset building for future model training and easy integration with the existing REST API.

## Confirmed Approach

- **Detection Model:** YOLOv5 Nano (pre-trained) for initial leaf detection, chosen for its speed and efficiency on the Pi. Custom training will be considered if needed.
- **Image Processing:** OpenCV for image capture, preprocessing, and cropping detected leaf regions.
- **Dataset Building:** Cropped leaf images will be saved for dataset creation and future model training.
- **Pipeline Structure:** Modular, with clear separation between detection, cropping, classification (future), and API integration.
- **REST API:** Results will be exposed via the Flask REST API for integration with Home Assistant and other systems.

## Pipeline Plan

1. **Image Capture:** Use the Pi camera to capture plant images.
2. **Leaf Detection:** Run YOLOv5 Nano to detect leaves in the captured image.
3. **Cropping:** Use OpenCV to crop detected leaf regions.
4. **Dataset Building:** Save cropped images for dataset creation and labeling during the prototyping phase. Once a sufficient dataset is collected and a custom model is trained, saving crops can be disabled to conserve disk space.
5. **(Optional) Health Classification:** Add a classifier for leaf health status in a future phase (e.g., using TensorFlow Lite or custom model).
6. **REST API Integration:** Expose detection/cropping results via Flask REST API.

## Implementation Steps

1. **Prototype Detection & Cropping:**
   - Capture a frame from the Pi webcam on demand using OpenCV.
   - Run YOLOv5 Nano (pre-trained) on the captured frame to detect leaves.
   - Use OpenCV to crop detected regions and save them to disk automatically.
   - Expose a Flask endpoint (`/plant_health/capture_and_detect`) to trigger this process both manually (from Home Assistant) and automatically (via daily cron job or scheduled task).
2. **Dataset Building:**
   - Organize and label cropped images for future training.
   - Saving crops is only required during the initial prototyping/dataset-building phase. After model training, disable or limit crop saving to conserve disk space.
3. **Evaluate Detection:**
   - Assess detection accuracy; if needed, plan for custom training.
4. **Integrate with REST API:**
   - Add endpoints to serve detection/cropping results.
5. **Document Findings:**
   - Record results, issues, and improvements in `.specs/docs/plant-health-check-findings.md`.
6. **Debugging & Iteration:**
   - Track issues in `.specs/debugging/plant-health-check-debugging.md` and iterate as needed.

## Next Steps

- Begin with prototyping detection and cropping using the pre-trained YOLOv5 Nano model and OpenCV.
- Save cropped images for dataset building.
- Document progress and findings in the appropriate `.specs` files.
