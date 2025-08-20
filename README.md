# Pi-Pico Smart Monitor

This project is a smart monitoring system using a Raspberry Pi (3B) and a Raspberry Pi Pico (or Pico W) for home and plant environment monitoring. It features:

- **Raspberry Pi**: Runs a Flask server to provide a REST API for sensor data and a webcam video stream. Integrates with Home Assistant for smart home dashboards.
- **Raspberry Pi Pico**: Reads temperature, humidity, and soil moisture sensors, displays data on an LCD, and sends readings to the Pi via USB serial.
- **Home Assistant Integration**: RESTful sensor configuration allows real-time monitoring of plant and environment data in Home Assistant dashboards.

## Features

- Live webcam streaming from the Pi
- REST API endpoint for sensor data: `/pico/sensors` (returns JSON with `temp`, `humi`, `moisture`)
- LCD display and RGB LED feedback on the Pico
- Soil moisture alerting and visual feedback
- WiFi and static IP configuration for flexible deployment
- Systemd and cron job options for auto-starting the server on boot

## Folder Structure

- `pi/` — Flask server, REST API, and webcam code for the Raspberry Pi
- `pico/` — MicroPython code for the Pico, including sensor reading and serial communication
- `.specs/` — Project plans, troubleshooting, and documentation

## Getting Started

1. Flash the Pico with the MicroPython firmware and upload the code in `pico/`.
2. Set up the Pi with Python, Flask, and OpenCV (`pip install flask opencv-python`).
3. Configure WiFi and static IP using netplan if needed.
4. Start the Flask server (`python3 pi/main.py`) or set up auto-start with cron or systemd.
5. Integrate with Home Assistant using the RESTful sensor configuration.

## REST API Example

```
GET http://<pi-ip>:5000/pico/sensors
Response: {"temp": 20, "humi": 60, "moisture": 1}
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
