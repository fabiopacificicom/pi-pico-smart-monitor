
# Plant Health Check Feature — Task Log

Track all tasks, progress, and notes for the plant health check implementation.

## Task Checklist

- [x] Research and select object detection model for leaf detection  
 **Decision:** Use YOLOv5 Nano for leaf detection (fast, accurate, Pi-friendly)
- [ ] Implement on-demand plant health check:
  - Capture frame from webcam
  - Run YOLOv5 Nano detection
  - Crop and save detected leaves (required during prototyping/dataset-building; disable or limit after model training to conserve disk space)
  - Expose Flask endpoint `/plant_health/capture_and_detect` (triggerable both manually from Home Assistant and automatically via daily cron)
- [ ] Select and prepare TFLite plant disease model
- [ ] Integrate TFLite model inference for cropped leaves
- [ ] Optimize performance (timing, threading)
- [ ] Integrate with Home Assistant
- [ ] Test with real plant images
- [ ] Document findings and update specs

---

Add new tasks, notes, and completion dates as you progress.
