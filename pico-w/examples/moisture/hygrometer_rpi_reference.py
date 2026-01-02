"""
Reference Raspberry Pi script from the module documentation.
This is included as a verbatim reference so you can compare behavior
with the Pico W implementation.

Wiring (as in the doc):
  - D0  -> GPIO18 (BCM numbering)
  - GND -> GND
  - VCC -> 3V3

Run on Raspberry Pi (Raspbian):
  sudo apt-get update && sudo apt-get upgrade
  sudo apt-get install python3-rpi.gpio
  python3 hygrometer_rpi_reference.py
"""

import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DIGIOUT = 18
GPIO.setup(DIGIOUT, GPIO.IN)

time.sleep(2)
print('[Press CTRL + C to end the script!]')
try:
    # Main program loop
    while True:
        if GPIO.input(DIGIOUT) == 0:
            print('Soil moisture level: HIGH')
        else:
            print('Soil moisture level: LOW')
        time.sleep(2)
except KeyboardInterrupt:
    print('\nScript end!')
finally:
    GPIO.cleanup()
