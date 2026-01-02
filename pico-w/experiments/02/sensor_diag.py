"""Sensor diagnostic for Experiment 02 (Pico W)

Run this on the Pico to observe ADC raw values, a small moving-average
(smoothed) value, and the digital DO pin. Useful for step-1 verification.

Usage:
- Copy this file to the Pico and run it from REPL, or
- From REPL: from sensor_diag import main; main()

"""

import time
from machine import Pin, ADC

# Configuration
ADC_PIN = 26
DIGITAL_SENSOR_PIN = 18
SAMPLE_INTERVAL = 0.5  # seconds
MA_WINDOW = 6


def main():
    adc = ADC(Pin(ADC_PIN))
    try:
        digital = Pin(DIGITAL_SENSOR_PIN, Pin.IN, Pin.PULL_DOWN)
    except TypeError:
        digital = Pin(DIGITAL_SENSOR_PIN, Pin.IN)

    buf = []
    try:
        while True:
            raw = adc.read_u16()
            buf.append(raw)
            if len(buf) > MA_WINDOW:
                buf.pop(0)
            smoothed = sum(buf) // len(buf)
            ts = int(time.time())
            print('ts:', ts, 'raw:', raw, 'smoothed:', smoothed, 'digital:', digital.value())
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print('Stopped by user')
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
