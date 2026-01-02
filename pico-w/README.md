# PI-Pico-W Watering Controller

[← Back to main documentation](../README.md) | [Pi documentation](../pi/README.md) | [Pico documentation](../pico/README.md)

This folder contains the code for the Raspberry Pi Pico-W device used in the plant watering system. The Pico-W acts as a WiFi-enabled controller that receives soil moisture data from the central Pi and controls a relay (for a water pump or valve) accordingly.

## Features

- **WiFi Connectivity:**
 	- Connects to a local WiFi network using provided SSID and password.

- **Remote Sensor Monitoring:**
 	- Periodically fetches real-time sensor data (moisture, etc.) from the central Pi via a REST API endpoint (HTTP GET).

- **Automated Watering Control:**
 	- Controls a relay (connected to GP15) to turn the water pump ON or OFF based on the received soil moisture value:
  		- Relay ON (watering): Soil is dry (`moisture == 0`)
  		- Relay OFF: Soil is wet (`moisture == 1`)
 	- Fails safe (relay OFF) if data is missing or errors occur.

- **Status Logging:**
 	- Prints connection status, sensor data, and relay actions to the serial console for debugging.

## Hardware Connections

| Component         | Pico-W Pin | Notes                        |
|-------------------|------------|------------------------------|
| Relay Module      | GPIO15     | IN pin (active low relay)    |

## Code Structure

- `main.py`: Main application loop. Handles WiFi connection, REST API polling, and relay control logic.
 	- **WiFi Setup:** Connects to WiFi and prints IP address.
 	- **REST API Fetch:** Uses `urequests` to get sensor data from the Pi.
 	- **Relay Logic:** Sets relay ON/OFF based on moisture value.
 	- **Error Handling:** Ensures relay is OFF if errors occur.

## Example Output

```
Connecting to WiFi...
Connected. IP: 192.168.1.101
Fetching sensor data...
Sensor data: {'temp': 25, 'humi': 60, 'moisture': 0}
Moisture value: 0
Relay ON (soil is dry)
```

## Usage

1. Connect the relay module to GPIO15 (IN pin) on the Pico-W.
2. Update `SSID`, `PASSWORD`, and `SENSOR_URL` in `main.py` as needed.
3. Flash `main.py` to the Pico-W.
4. Power the Pico-W and monitor the serial output for status.

## Troubleshooting

- If WiFi does not connect, check SSID/PASSWORD and signal strength.
- If relay does not activate, check wiring and relay module type.
- If no sensor data is received, verify the Pi's REST API endpoint and network connectivity.

## Device configuration (`pico-w/config.py`)

Configuration that may vary per-device is provided via a local `config.py` file on the device.
Copy `pico-w/config.py.example` to the device as `pico-w/config.py` (or `config.py` at the device root) and edit the values there. Do NOT commit your device `config.py` to the repository.

Key fields available in the example:
- Hardware pins: `ADC_PIN`, `DIGITAL_SENSOR_PIN`, `RELAY_PIN`
- Calibration: `DRY_ADC`, `WET_ADC`, `SENSOR_RAW_DISCONNECTED`, `SENSOR_RAW_DISCONNECTED_LOW`
- Sampling / smoothing: `MA_WINDOW`, `SAMPLE_INTERVAL`
- Thresholds: `START_WATER_PERCENT`, `STOP_WATER_PERCENT`
- Safety / timing: `MAX_WATERING_TIME`, `MIN_INTERVAL_BETWEEN_WATERING`, `BOOT_DELAY_SECONDS`
- Telemetry / Wi-Fi: `ENABLE_WIFI`, `WIFI_SSID`, `WIFI_PASSWORD`, `TELEMETRY_URL`, `TELEMETRY_INTERVAL`

Usage on-device:
1. Create `pico-w/config.py` on the device filesystem with the desired values.
2. Reboot the Pico‑W so `main.py` picks up the new configuration.

See `pico-w/config.py.example` for a full list of configurable defaults.

## License

MIT License. See main project for details.
