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

Add a RESTful sensor in Home Assistant to call the endpoint and display results. Example configuration (add to your `configuration.yaml`):

```yaml
sensor:
 - platform: rest
  name: Plant Health Check
  resource: "http://<PI_IP>:5050/plant_health/capture_and_detect"
  method: GET
  scan_interval: 3600  # Check every hour (or set to 86400 for once per day)
  value_template: "{{ value_json.status }}"
  json_attributes:
   - num_crops
   - crops
  timeout: 60
```

Replace `<PI_IP>` with your Pi's IP address. This sensor will show the status and number of crops; you can use the attributes in a dashboard card or automation.

## 7. Automate with Cron (Optional)

To trigger the health check automatically every hour between 3:00 PM and 7:00 AM (overnight and afternoon), add the following lines to your crontab (`crontab -e`):

```
0 15-23 * * * curl -s http://127.0.0.1:5050/plant_health/capture_and_detect
0 0-7   * * * curl -s http://127.0.0.1:5050/plant_health/capture_and_detect
```

This will run the check at the start of every hour from 15:00 to 07:00. Adjust as needed for your use case.

## 8. Notes

- The first run will download YOLOv5 weights (requires internet).
- For dataset building, crops are saved on every trigger. You can disable this later for production.
- Check the `leaf_crops/` folder for results and manage disk space as needed.

---

For troubleshooting or advanced configuration, see the main project specs or contact the maintainer.
