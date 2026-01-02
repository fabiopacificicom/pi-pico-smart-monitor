# PI-Pico Plant Monitoring Device

[← Back to main documentation](../README.md) | [Pi documentation](../pi/README.md) | [Pico W documentation](../pico-w/README.md)

This folder contains the code for the Raspberry Pi Pico device used in the plant watering and monitoring system. The Pico is responsible for reading environmental sensors, displaying information, and communicating with the central Raspberry Pi (Pi) for monitoring and automation.

## Features

- **Sensor Integration:**
 	- Reads temperature and humidity from a DHT11 sensor (GPIO1).
 	- Reads soil moisture from a digital moisture sensor (GPIO14).

- **Display:**
 	- Shows status and alerts on a 16x2 I2C LCD (address 0x27, SCL=GPIO5, SDA=GPIO4).

- **Visual Alerts:**
 	- Controls a WS2812B RGB LED (data on GPIO15) to indicate plant status:
  		- Green: Temperature in optimal range (20–30°C)
  		- Red: High temperature (>30°C)
  		- Blue: Low temperature (<20°C)
  		- Orange (flashing): Soil is dry

- **Data Sharing:**
 	- Sends sensor data (temperature, humidity, moisture) to the central Pi via USB serial as CSV lines (see `pico_data_share.py`).

## Hardware Connections

| Component         | Pico Pin | Notes                        |
|-------------------|----------|------------------------------|
| DHT11 Sensor      | GPIO1    | Data pin                     |
| Moisture Sensor   | GPIO14   | Digital output, PULL_UP      |
| LCD1602 (I2C)     | GPIO4/5  | SDA=GPIO4, SCL=GPIO5, Addr=0x27 |
| WS2812B LED       | GPIO15   | Data input                   |

## Code Structure

- `main.py`: Main application loop. Handles sensor reading, display updates, LED control, and data transmission.
 	- **DHT11 Reading:** Bit-banged protocol for temperature/humidity.
 	- **LCD Driver:** Minimal I2C driver for 16x2 display.
 	- **WS2812B Driver:** PIO-based driver for RGB LED.
 	- **Moisture Logic:** Alerts and display logic for dry/wet soil.
 	- **Data Sharing:** Calls `pico_data_share.send_status()` to transmit readings.

- `pico_data_share.py`: Simple module to send sensor data to the Pi over USB serial. Outputs CSV lines (e.g., `25,60,1`).

## Example Output

```
T:25C H:60%      # LCD line 1
Moisture: Wet    # LCD line 2

25,60,1          # USB serial output to Pi (temp, humi, moisture)
```

## Usage

1. Connect the sensors and peripherals as described above.
2. Flash the `main.py` and `pico_data_share.py` files to the Pico.
3. Connect the Pico to the Pi via USB. The Pi can read serial output for monitoring.
4. The LCD and LED will provide real-time feedback and alerts.

## Troubleshooting

- If the LCD does not display, check I2C wiring and address.
- If the LED does not light up, check data pin and power.
- If no data is received on the Pi, ensure the correct serial port is used.

## License

MIT License. See main project for details.
