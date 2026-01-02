"""Sensor + Relay test for Experiment 02

Run this on the Pico to test relay triggering from the moisture sensor.
- Prints raw, smoothed, percent, digital, and relay state each loop
- Turns relay ON when percent <= START_WATER_PERCENT and OFF when >= STOP_WATER_PERCENT
- Treats raw==0 or raw>=65535 as sensor fault and forces relay OFF

Usage:
from sensor_relay_test import main
main()

Ctrl-C to stop; relay is turned off on exit.
"""

import time
from machine import Pin, ADC

# Config (adjust as needed)
ADC_PIN = 26
DIGITAL_SENSOR_PIN = 18
RELAY_PIN = 15
RELAY_ACTIVE_LOW = True
# Calibrated from your diagnostic run:
# - dry soil (inserted, very dry) ~36k
# - wet soil ~15k-19k
# Use dry soil value as DRY_ADC and wet soil as WET_ADC so air/disconnect
# (near full-scale) is treated as a fault and won't trigger watering.
DRY_ADC = 37000
WET_ADC = 15000
# Reduce smoothing window for faster response during tests
MA_WINDOW = 4
START_WATER_PERCENT = 30
STOP_WATER_PERCENT = 60
# Faster sampling for interactive testing
SAMPLE_INTERVAL = 0.5
# Treat values near full-scale as disconnected (air/unplugged)
SENSOR_RAW_DISCONNECTED = 65000
SENSOR_RAW_DISCONNECTED_LOW = 0
REQUIRED_CONSECUTIVE = 4


def percent_from_raw(raw):
    # clamp
    if raw > DRY_ADC:
        raw = DRY_ADC
    if raw < WET_ADC:
        raw = WET_ADC
    try:
        percent = (1 - (raw - WET_ADC) / float(DRY_ADC - WET_ADC)) * 100.0
    except ZeroDivisionError:
        percent = 0.0
    if percent < 0:
        percent = 0.0
    if percent > 100:
        percent = 100.0
    return percent


class Relay:
    def __init__(self, pin_no, active_low=True):
        self.pin_no = pin_no
        self.pin = Pin(pin_no, Pin.OUT)
        self.active_low = active_low
        # internal state to track relay when pin may be set to input
        self._state = False
        self.off()

    def on(self):
        # ensure pin configured as output and drive active level
        try:
            self.pin.init(Pin.OUT)
        except Exception:
            pass
        self.pin.value(0 if self.active_low else 1)
        self._state = True

    def off(self):
        # Use the same approach as relay_test: set pin to input to "disconnect" IN
        # which some relay modules expect for OFF.
        try:
            self.pin.init(Pin.IN)
        except Exception:
            # fallback to driving inactive level
            self.pin.init(Pin.OUT)
            self.pin.value(1 if self.active_low else 0)
        self._state = False

    def is_on(self):
        return bool(self._state)


def main():
    adc = ADC(Pin(ADC_PIN))
    try:
        digital = Pin(DIGITAL_SENSOR_PIN, Pin.IN, Pin.PULL_DOWN)
    except TypeError:
        digital = Pin(DIGITAL_SENSOR_PIN, Pin.IN)

    relay = Relay(RELAY_PIN, active_low=RELAY_ACTIVE_LOW)

    buf = []
    watering = False
    watering_start = 0
    low_count = 0

    try:
        while True:
            raw_latest = adc.read_u16()
            buf.append(raw_latest)
            if len(buf) > MA_WINDOW:
                buf.pop(0)
            # compute smoothed from valid samples only (exclude disconnect extremes)
            valid = [v for v in buf if SENSOR_RAW_DISCONNECTED_LOW < v < SENSOR_RAW_DISCONNECTED]
            dig = digital.value()
            # Fault detection on latest sample
            if raw_latest >= SENSOR_RAW_DISCONNECTED or raw_latest <= SENSOR_RAW_DISCONNECTED_LOW:
                print('FAULT: raw_latest=', raw_latest, 'digital=', dig, 'relay_on=', relay.is_on())
                if relay.is_on():
                    relay.off()
                    watering = False
                time.sleep(SAMPLE_INTERVAL)
                continue
            if not valid:
                # no valid samples yet (buffer contained only invalid extremes)
                print('FAULT_BUFFER: no valid samples; raw_latest=', raw_latest, 'relay_on=', relay.is_on())
                if relay.is_on():
                    relay.off()
                    watering = False
                low_count = 0
                time.sleep(SAMPLE_INTERVAL)
                continue
            raw_smoothed = sum(valid) // len(valid)
            percent = percent_from_raw(raw_smoothed)

            # Control logic
            if not watering:
                if percent <= START_WATER_PERCENT:
                    low_count += 1
                    print('Consecutive low readings:', low_count)
                    if low_count >= REQUIRED_CONSECUTIVE:
                        print('ACTION: Start watering (percent={:.1f})'.format(percent))
                        relay.on()
                        watering = True
                        watering_start = time.time()
                        low_count = 0
                else:
                    low_count = 0
            else:
                if percent >= STOP_WATER_PERCENT:
                    print('ACTION: Stop watering (percent={:.1f})'.format(percent))
                    relay.off()
                    watering = False
                # safety max (10s) during tests
                elif time.time() - watering_start >= 10:
                    print('ACTION: Stop watering (max test time reached)')
                    relay.off()
                    watering = False

            print('raw_latest:', raw_latest, 'smoothed:', raw_smoothed, 'percent:{:.1f}'.format(percent), 'digital:', dig, 'relay_on:', relay.is_on())
            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print('Stopped by user; turning relay off')
        relay.off()
    except Exception as e:
        print('Error:', e)
        relay.off()


if __name__ == '__main__':
    main()
