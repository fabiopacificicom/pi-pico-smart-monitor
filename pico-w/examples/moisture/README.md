# AZ-Delivery Hygrometer (example)

This folder contains simple example scripts to test the AZ-Delivery Hygrometer v1.0 Module's digital output.

Files:
- `hygrometer_rpi_reference.py`: verbatim reference script from the module documentation (Raspberry Pi / RPi.GPIO).
- `hygrometer_pico.py`: MicroPython example for the Raspberry Pi Pico W (digital input).

Wiring summary

- Module VCC -> 3V3
- Module GND -> GND
- Module D0  -> Pico GP18 (or Raspberry Pi BCM18 for the RPi script)

Notes and testing

- The module offers both analog and digital outputs. These examples use the digital output (D0).
- The module documentation example treats `D0 == 0` as "HIGH" moisture; the scripts follow the same logic. If you observe inverted behavior on your hardware, invert the condition in the script.
- To test on the Pico W: copy `hygrometer_pico.py` to the device and run it with Thonny or as `main.py`. Monitor serial output.
- To test on a Raspberry Pi: install `python3-rpi.gpio` and run `hygrometer_rpi_reference.py`.

Next steps for Experiment 02

- Once you confirm the sensor works with the Pico W, tell me and I will:
  - refactor `pico-w/experiments/01/01-main.py` to read the local digital (or analog) sensor directly,
  - add debouncing/hysteresis and optional ADC thresholding if you prefer the analog path,
  - keep the existing safety limits (`MAX_WATERING_TIME`, `COOLDOWN_PERIOD`) and integrate the new sensor input logic.
