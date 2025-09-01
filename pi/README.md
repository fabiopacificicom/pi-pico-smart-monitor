# Pi Central Server & Webcam Streaming

[← Back to main documentation](../README.md) | [Pico documentation](../pico/README.md) | [Pico W documentation](../pico-w/README.md)

This folder contains the code for the central Raspberry Pi server in the plant monitoring and watering system. The Pi acts as a hub, collecting sensor data from the Pico, providing a REST API for the Pico-W, and streaming live video from a connected webcam.

## Features

- **Webcam Streaming:**
  - Streams live video from the Pi's webcam to any browser on the network.
  - Main page (`/`) displays the video stream and a status dashboard.

- **Sensor Data API:**
  - Receives real-time temperature, humidity, and soil moisture data from the Pico over USB serial.
  - Exposes the latest sensor readings via a REST API (`/pico/sensors`) for use by the Pico-W or other clients.

## Additional Features

- **Plant Health & Leaf Detection API:**
  - On-demand leaf detection and cropping using YOLOv5 Nano (see `prototype_leaf_detection.py`).
  - Captures a frame from the webcam, detects leaves, and saves crops to `leaf_crops/`.
  - Exposes endpoints for remote triggering and crop retrieval.

- **Leaf Detection & Prototyping:**
  - Includes scripts for leaf detection and plant health analysis (see `prototype_leaf_detection.py`, `models/`, and `test_images/`).

## Requirements

### Core Requirements

- Python 3.x
- Flask
- OpenCV (`cv2`)
- PySerial (`serial`) for USB communication

### Plant Health Features

- PyTorch (`torch`)
- TorchVision (`torchvision`)
- YOLOv5 (auto-downloaded from Torch Hub)

Install basic dependencies with:

```bash
pip install flask opencv-python pyserial
```

For plant health features, install:

```bash
pip install torch torchvision
```

## Project Structure

- `main.py` / `pi_webcam_main.py`: Flask server for video streaming and dashboard.
- `sensors_data_api.py`: Handles USB serial communication with the Pico and provides the `/pico/sensors` API endpoint.
- `prototype_leaf_detection.py`: Experimental code for plant/leaf analysis.
- `models/`, `test_images/`, `leaf_crops/`: Supporting data and models for plant health features.

## API Endpoints

### `/` (GET)

- Serves the main dashboard page with live webcam stream and status info.

### `/video_feed` (GET)

- Streams MJPEG video from the Pi's webcam for embedding in the dashboard.

### `/plant_health/capture_and_detect`

- **Method:** GET or POST
- **Description:**
  - Captures a frame from the webcam and runs YOLOv5 Nano detection.
  - Crops detected leaves (or grid crops if no detection) and saves them to `leaf_crops/`.
  - Returns a JSON response with the number of crops and their URLs.
  - Example response:

    ```json
    {
      "status": "ok",
      "num_crops": 4,
      "crops": ["/crops/capture_crop_0_leaf.jpg", ...]
    }
    ```

### `/crops/<filename>`

- **Method:** GET
- **Description:**
  - Serves a cropped leaf image from the `leaf_crops/` directory by filename.
  - Used to retrieve images listed in the `/plant_health/capture_and_detect` response.

### `/pico/sensors` (GET)

- Returns the latest sensor data as JSON, e.g.:

- The `/plant_health/capture_and_detect` endpoint can be triggered remotely (e.g., via HTTP POST) to analyze the current webcam frame for leaves and save crops.

- Cropped images are accessible via `/crops/<filename>`.

  ```json  
  { "temp": 25.0, "humi": 60.0, "moisture": 1 }

  ```

- Data is updated in real time as the Pico sends new readings over USB serial.

## How It Works

1. The Pico device connects via USB and sends sensor data as CSV lines.
2. The Pi reads this data, updates the latest values, and serves them via the `/pico/sensors` API.
3. The Pico-W polls this API to decide when to activate the water pump.

To trigger leaf detection and get crop URLs:

```bash
curl -X POST http://<raspberry-pi-ip>:5000/plant_health/capture_and_detect
```

To view a crop:
Url: "http://<raspberry-pi-ip>:5000/crops/<filename>"

```bash
curl -X GET http://<raspberry-pi-ip>:5000/crops/<filename>
```

4. The Flask server streams video from the webcam to the dashboard.

## Usage

1. Connect a USB webcam to the Pi and ensure it is accessible (e.g., `/dev/video0`).
2. Connect the Pico via USB for sensor data.
3. Run the server:

```bash
python main.py
```

1. Open a browser to `http://<raspberry-pi-ip>:5000/` to view the dashboard and video stream.

## Notes

- The server listens on all interfaces (`0.0.0.0`) by default.
- Ensure the correct serial port is used for Pico data (see `sensors_data_api.py`).
- For plant health features, see the `prototype_leaf_detection.py` and `models/` folder.

## License

MIT License. See main project for details.
