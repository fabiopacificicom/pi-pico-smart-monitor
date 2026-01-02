# Plant Health Check Prototype: Setup Guide

This guide explains how to set up and run the prototype leaf detection pipeline on your Raspberry Pi.

---

## 1. Prerequisites

- Raspberry Pi with camera/webcam connected and enabled
- Python 3.8+
- Internet connection (for first YOLOv5 model download)

## 2. Install Required Packages

Run the following commands in your Pi terminal:

```bash
sudo apt update
sudo apt install python3-pip python3-opencv libopencv-dev
pip3 install torch torchvision flask opencv-python ultralytics seaborn
```

## 3. Download the Code

- Place `prototype_leaf_detection.py` in your desired directory (e.g., `~/pi/`)
- Ensure the `leaf_crops/` directory exists (the script will create it if missing)

## 4. Run the Flask Server

From the directory containing `prototype_leaf_detection.py`:

```bash
python3 prototype_leaf_detection.py
```

- The server will start on port 5050 by default.

## 5. Test the Endpoint

- Open a browser or use `curl` to trigger a detection:

```bash
curl http://<PI_IP>:5050/plant_health/capture_and_detect
```

- The response will show the number of crops and their file paths.
- Cropped images will be saved in the `leaf_crops/` directory.

## 6. Integrate with Home Assistant (Optional)

### Home Assistant Integration: Thumbnails and Trigger Button

Add a RESTful sensor in Home Assistant to call the endpoint and display results. Example configuration (add to your `configuration.yaml`):

```yaml

# Plant Health Check Setup Guide

## Overview

This guide explains how to set up the plant health check pipeline on your Raspberry Pi, integrate it with Home Assistant, and automate the process of capturing, cropping, and labeling plant images for dataset building and monitoring.

**Key Features:**
- Automated image capture and disease detection using YOLOv5 Nano
- REST API for triggering detection and serving crop images
- Home Assistant integration for automation and UI (thumbnails, trigger button)
- Browser-based crop viewing and labeling

---

## 1. Prerequisites

- Raspberry Pi with camera module
- Python 3.8+
- Flask, OpenCV, YOLOv5 Nano (see `requirements.txt`)
- Home Assistant (core or OS)

---

## 2. Running the Plant Health Server

1. On your Raspberry Pi, run the Flask server:
   ```bash
   python3 main.py
   # or
   python3 prototype_leaf_detection.py
   ```

   By default, the server runs on port 5000.

2. The API exposes:
   - `POST /plant_health/capture_and_detect` — triggers capture, detection, and crop saving
   - `GET /crops/<filename>` — serves crop images

---

## 3. Home Assistant Integration (configuration.yaml)

Add the following to your `configuration.yaml` to enable full backend integration. This setup covers all possible automation and UI backend elements that can be handled via YAML. For advanced UI (gallery, dynamic thumbnails), see the Lovelace section below.

### RESTful Sensor (fetch crop list and count)

```yaml
sensor:
  - platform: rest
    name: Plant Crop List
    resource: http://<PI_IP>:5000/plant_health/capture_and_detect
    method: POST
    scan_interval: 3600  # every hour, or adjust as needed
    value_template: "{{ value_json.crops | length }}"
    json_attributes:
      - crops
```

### REST Command (trigger detection)

```yaml
rest_command:
  plant_health_capture:
    url: "http://<PI_IP>:5000/plant_health/capture_and_detect"
    method: POST
```

### Input Button (for manual trigger)

```yaml
input_button:
  plant_health_capture:
    name: Capture Plant Health
```

### Automation (trigger detection from button)

```yaml
automation:
  - alias: "Capture Plant Health on Button Press"
    trigger:
      - platform: state
        entity_id: input_button.plant_health_capture
    action:
      - service: rest_command.plant_health_capture
```

### Generic Camera (show latest crop image)

```yaml
camera:
  - platform: generic
    name: Latest Plant Crop
    still_image_url: >
      http://<PI_IP>:5000/crops/{{ state_attr('sensor.plant_crop_list', 'crops')[-1] if state_attr('sensor.plant_crop_list', 'crops') }}
    content_type: image/jpeg
```

---

## 4. Lovelace UI (manual step)

The following UI elements must be added via the Lovelace dashboard editor (not possible in configuration.yaml):

### Button Card (trigger detection)

```yaml
type: button
name: Capture Plant Health
entity: input_button.plant_health_capture
show_state: false
tap_action:
  action: call-service
  service: rest_command.plant_health_capture
```

### Entity Card (show crop count)

```yaml
type: entity
entity: sensor.plant_crop_list
name: Crop Count
```

### Picture Entity Card (show latest crop)

```yaml
type: picture-entity
entity: camera.latest_plant_crop
name: Latest Plant Crop
```

### (Optional) Manual Crop Gallery

For a gallery of all crops, you can manually add multiple `picture` cards, or use a custom card (e.g., [gallery-card](https://github.com/TarheelGrad/gallery-card)) and point to the crop URLs from the REST sensor attributes. Dynamic galleries require a custom card or manual YAML editing in the dashboard.

---

## 5. Automation via Cron (optional)

You can also automate detection on a schedule using cron on the Pi:

```cron
0 * * * * curl -X POST http://localhost:5000/plant_health/capture_and_detect
```

---

## 6. Browser-Based Labeling

Open `http://<PI_IP>:5000/crops/<filename>` in your browser to view and label crops. You can build a simple HTML/JS page to display and label images using the crop URLs from the REST API.

---

## 7. Troubleshooting

- Ensure the Flask server is running and accessible from Home Assistant.
- Replace `<PI_IP>` with your Pi's actual IP address.
- Check Home Assistant logs for REST sensor/command errors.
- For advanced UI (dynamic gallery), use Lovelace custom cards or manual configuration.

---

## 8. References

- [Home Assistant RESTful Sensor](https://www.home-assistant.io/integrations/rest/)
- [Home Assistant REST Command](https://www.home-assistant.io/integrations/rest_command/)
- [Home Assistant Generic Camera](https://www.home-assistant.io/integrations/camera.generic/)
- [Lovelace Gallery Card](https://github.com/TarheelGrad/gallery-card)

---

This guide provides a complete backend YAML setup for the plant health check pipeline. For advanced UI, use the Lovelace dashboard editor or custom cards as described above. All backend automation and integration is handled via configuration.yaml; only the UI gallery and dynamic image display require manual steps in the dashboard.
