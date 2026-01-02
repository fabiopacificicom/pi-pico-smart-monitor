# Pi Pico W IR Sensor Test Script
# Reads the IR sensor on GPIO 21 and prints its value.
# (This script does NOT decode IR remote codes, just prints digital state changes.)

from machine import Pin
import time

IR_SENSOR_PIN = 21
ir_sensor = Pin(IR_SENSOR_PIN, Pin.IN)

print("IR sensor test: Press buttons on the remote and watch for value changes.")

try:
    last_value = ir_sensor.value()
    while True:
        value = ir_sensor.value()
        if value != last_value:
            print(f"IR sensor changed! Previous: {last_value}, Now: {value}")
            last_value = value
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Test stopped.")
