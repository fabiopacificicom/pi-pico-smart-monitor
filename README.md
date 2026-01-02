# Pi-Pico Smart Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/fabiopacificicom/pi-pico-smart-monitor)](https://github.com/fabiopacificicom/pi-pico-smart-monitor/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

This project is a comprehensive plant monitoring and watering automation system using a three-component architecture:

- **Raspberry Pi (Hub)**: Central server providing webcam streaming, sensor data API, and plant health analysis using computer vision.
- **Raspberry Pi Pico (Sensors)**: Reads environmental data (temperature, humidity, soil moisture), provides visual feedback via LCD and RGB LED.
- **Raspberry Pi Pico W (Controller)**: WiFi-enabled watering controller that activates a pump/valve based on sensor data from the hub.

## Features

### Monitoring & Analysis

- Live webcam streaming with plant health analysis
- Automated leaf detection and crop analysis using YOLOv5
- Environmental sensor data tracking (temperature, humidity, soil moisture)
- Visual feedback through LCD display and RGB LED indicators

### Automation & Control

- Smart watering system with configurable thresholds
- Relay control for water pump/valve automation
- Real-time moisture level monitoring and alerts
- Fail-safe operation with error handling

### Integration & API

- Complete REST API for sensor data and plant analysis
- Home Assistant integration for smart home dashboards
- USB serial and WiFi communication between components
- Configurable deployment with systemd/cron support

## Component Documentation

### [`pi/`](pi/README.md) — Central Hub
- Flask server for webcam streaming and API
- YOLOv5-based leaf detection
- Real-time video streaming
- Data collection from Pico
- [View Pi documentation →](pi/README.md)

### [`pico/`](pico/README.md) — Sensor Module
- Temperature/humidity (DHT11) monitoring
- Soil moisture sensing
- LCD status display
- RGB LED indicators
- USB serial communication
- [View Pico documentation →](pico/README.md)

### [`pico-w/`](pico-w/README.md) — Watering Controller
- WiFi connectivity
- Relay control for water pump
- REST API integration
- Automated watering logic
- [View Pico W documentation →](pico-w/README.md)

### `.specs/` — Documentation and specifications
- Configuration examples
- Troubleshooting guides
- Component diagrams
  - Configuration examples
  - Troubleshooting guides
  - Component diagrams

## Getting Started

### 1. Set up the Sensor Module (Pico)

1. Flash MicroPython firmware to the Pico
2. Upload all files from `pico/` to the device
3. Connect sensors: DHT11 (GPIO1), moisture (GPIO14), LCD (I2C: GPIO4/5), LED (GPIO15)

### 2. Configure the Hub (Raspberry Pi)

1. Install dependencies:

   ```bash
   pip install flask opencv-python pyserial torch torchvision
   ```

2. Connect the Pico via USB
3. Start the server: `python3 pi/main.py`
4. Optional: Set up auto-start with systemd/cron

### 3. Prepare the Watering Module (Pico W)

1. Flash MicroPython firmware to the Pico W
2. Upload files from `pico-w/` to the device
3. Configure WiFi settings in `main.py`
4. Connect the relay module to GPIO15

### 4. Integration

1. Access the dashboard at `http://<pi-ip>:5000/`
2. Set up Home Assistant integration using the configuration below
3. Test the complete system:
   - Check sensor readings
   - Verify webcam stream
   - Test leaf detection
   - Confirm watering automation

## REST API Reference

### Sensor Data

```http
GET http://<pi-ip>:5000/pico/sensors
Response: {
  "temp": 20,
  "humi": 60,
  "moisture": 1
}
```

### Plant Health Analysis

```http
POST http://<pi-ip>:5000/plant_health/capture_and_detect
Response: {
  "status": "ok",
  "num_crops": 4,
  "crops": ["/crops/capture_crop_0_leaf.jpg", ...]
}
```

### Image Retrieval

```http
GET http://<pi-ip>:5000/crops/<filename>
Response: Binary image data (JPEG)
```

### Video Stream

```http
GET http://<pi-ip>:5000/video_feed
Response: MJPEG stream
```

## Home Assistant Example

The following configuration can be used to integrate the smart monitor with Home Assistant to display custom entities in the dashboard. To do that you need to edit your configuration.yaml file.

> replace <pi-ip> with the actual IP address of your Raspberry Pi
> for example: <http://192.168.1.10>

```yaml
# ...existing code...

sensor:
  - platform: rest
    name: "Happy Plants"
    resource: "http://<pi-ip>:5000/pico/sensors"
    method: GET
    scan_interval: 60  # Poll every 60 seconds
    timeout: 10
    value_template: "{{ value_json.moisture }}"
    json_attributes:
      - temp
      - humi
      - moisture
    headers:
      Content-Type: application/json

  - platform: template
    sensors:
      happy_plants_temperature:
        friendly_name: "Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.happy_plants', 'temp') }}"
      happy_plants_humidity:
        friendly_name: "Humidity"
        unit_of_measurement: "%"
        value_template: "{{ state_attr('sensor.happy_plants', 'humi') }}"
      happy_plants_moisture:
        friendly_name: "Moisture"
        value_template: >
          {% if state_attr('sensor.happy_plants', 'moisture')|int == 1 %}
            Wet
          {% else %}
            Dry
          {% endif %}

# ...existing code...

```

You can customise the sensor names and attributes as needed.

## Troubleshooting

See `.specs/` for configuration examples and troubleshooting.

## Authors

- @fabiopacifici and contributors

## License

MIT License
