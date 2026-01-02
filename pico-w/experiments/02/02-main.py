"""Experiment 02 - Pico W: Moisture-based pump controller

Wiring (see README):
- Relay VCC  -> Pico-W VBUS (5V)
- Relay GND  -> Pico-W GND
- Pico GP15  -> Relay IN (control)
- Pico-W VBUS -> Relay COM
- Pump +     -> Relay NO
- Pump -     -> Pico-W GND
- Sensor VCC -> Pico 3.3V
- Sensor GND -> Pico GND
- Sensor AO  -> Pico GP26 (ADC0 / A0)
- Sensor DO  -> Pico GP18 (digital out, optional)

This script reads the analog moisture sensor on GP26, applies a moving-average
filter, maps the reading to moisture percentage using configurable dry/wet
calibration values, and uses hysteresis (start at 30%, stop at 60% by default)
to control a relay on GP15 that powers the pump from VBUS.

Telemetry support exists but is disabled by default so the script can run
without any Wi-Fi credentials.
"""

import time
from machine import Pin, ADC

# Load device-local config early so constants can reference it safely
try:
    import config as device_config
except Exception as e:
    try:
        print('Device config import failed; using defaults. Error:', e)
    except Exception:
        pass
    device_config = None

# --- Configuration ---
# Load tunables from device-local `config.py` when present. Values below
# are the defaults and will be used when `pico-w/config.py` is not present.
# Pins
ADC_PIN = getattr(device_config, 'ADC_PIN', 26)            # GP26 / ADC0 / A0
DIGITAL_SENSOR_PIN = getattr(device_config, 'DIGITAL_SENSOR_PIN', 18) # optional digital out from sensor
RELAY_PIN = getattr(device_config, 'RELAY_PIN', 15)          # GP15 controls relay IN

# Digital sensor polarity: set to True if `1` means WET, False if `1` means DRY.
DIGITAL_WET_HIGH = getattr(device_config, 'DIGITAL_WET_HIGH', True)

# Relay polarity: True for active-LOW modules (IN=0 energizes)
RELAY_ACTIVE_LOW = getattr(device_config, 'RELAY_ACTIVE_LOW', True)

# Moisture calibration (u16 ADC, 0..65535)
# Based on diagnostics: dry soil (inserted) ~36k, wet soil ~15k-19k
DRY_ADC = getattr(device_config, 'DRY_ADC', 37000)
WET_ADC = getattr(device_config, 'WET_ADC', 15000)

# Smoothing
# Smaller window for more responsive behavior during testing
MA_WINDOW = getattr(device_config, 'MA_WINDOW', 4)

# Hysteresis thresholds (percent)
START_WATER_PERCENT = getattr(device_config, 'START_WATER_PERCENT', 30)   # start watering when percent <= this
STOP_WATER_PERCENT = getattr(device_config, 'STOP_WATER_PERCENT', 60)    # stop watering when percent >= this

# Startup & safety
BOOT_DELAY_SECONDS = getattr(device_config, 'BOOT_DELAY_SECONDS', 8)            # ignore automatic starts during initial boot
REQUIRED_CONSECUTIVE = getattr(device_config, 'REQUIRED_CONSECUTIVE', 4)         # consecutive low readings required to start
# treat saturated readings as sensor fault (air/unplugged)
SENSOR_RAW_DISCONNECTED = getattr(device_config, 'SENSOR_RAW_DISCONNECTED', 65000)
# Some ADCs or wiring faults can return 0 when disconnected; treat 0 as implausible too
SENSOR_RAW_DISCONNECTED_LOW = getattr(device_config, 'SENSOR_RAW_DISCONNECTED_LOW', 0)

# Safety timers (seconds)
# Default short max watering time to avoid long runs during tests
MAX_WATERING_TIME = getattr(device_config, 'MAX_WATERING_TIME', 3)     # maximum continuous watering time (seconds)
MIN_INTERVAL_BETWEEN_WATERING = getattr(device_config, 'MIN_INTERVAL_BETWEEN_WATERING', 30)  # min seconds between watering sessions

# Loop timing
SAMPLE_INTERVAL = getattr(device_config, 'SAMPLE_INTERVAL', 2.0)      # seconds between ADC samples

# Wi-Fi / Telemetry (configurable via pico-w/config.py on device)

# Defaults will be used when `pico-w/config.py` is not present on the device.
ENABLE_WIFI = getattr(device_config, 'ENABLE_WIFI', True)
TELEMETRY_INTERVAL = getattr(device_config, 'TELEMETRY_INTERVAL', 60)
WIFI_SSID = getattr(device_config, 'WIFI_SSID', '')
WIFI_PASSWORD = getattr(device_config, 'WIFI_PASSWORD', '')
TELEMETRY_URL = getattr(device_config, 'TELEMETRY_URL', 'http://<PI_IP>:5000/pico/sensors')

try:
    import urequests as requests
    import ujson as json
except Exception:
    requests = None
    import json


class Relay:
    def __init__(self, pin_no, active_low=True):
        # remember pin number so we can re-init mode as needed
        self.pin_no = pin_no
        self.pin = Pin(pin_no, Pin.OUT)
        self.active_low = active_low
        # Internal state; some relay modules expect IN to be left floating (input)
        # to represent OFF. Track state instead of relying on pin.value() when
        # the pin may be configured as input.
        self._state = False
        # Safe default: pump OFF
        self.off()
        try:
            print('Relay init: pin={}, active_low={}, state={}'.format(pin_no, self.active_low, self._state))
        except Exception:
            pass

    def on(self):
        # ensure pin configured as output and drive active level
        try:
            self.pin.init(Pin.OUT)
        except Exception:
            pass
        self.pin.value(0 if self.active_low else 1)
        self._state = True

    def off(self):
        # Many relay modules are turned OFF when IN is left floating. Use the
        # same approach as the working relay test: set pin to input to
        # effectively disconnect the control line. Fall back to driving the
        # inactive level if init-to-input is not supported.
        try:
            self.pin.init(Pin.IN)
        except Exception:
            try:
                self.pin.init(Pin.OUT)
            except Exception:
                pass
            self.pin.value(1 if self.active_low else 0)
        self._state = False

    def is_on(self):
        return bool(self._state)


class MoistureSensor:
    def __init__(self, adc_pin, digital_pin=None, ma_window=6):
        self.adc = ADC(Pin(adc_pin))
        # Try to enable an internal pull to avoid floating when sensor DO disconnected
        if digital_pin is not None:
            try:
                self.digital = Pin(digital_pin, Pin.IN, Pin.PULL_DOWN)
            except TypeError:
                # Some ports may not accept pull argument; fall back
                self.digital = Pin(digital_pin, Pin.IN)
        else:
            self.digital = None
        self.window = ma_window
        self.buf = []

    def read_raw(self):
        return self.adc.read_u16()

    def read_smoothed(self):
        raw = self.read_raw()
        self.buf.append(raw)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        # filter out implausible extremes from the smoothing buffer
        valid = [v for v in self.buf if SENSOR_RAW_DISCONNECTED_LOW < v < SENSOR_RAW_DISCONNECTED]
        if not valid:
            return None
        return sum(valid) // len(valid)

    def read_percent(self, raw=None):
        if raw is None:
            raw = self.read_smoothed()
        # clamp
        if raw > DRY_ADC:
            raw = DRY_ADC
        if raw < WET_ADC:
            raw = WET_ADC
        # Map raw value to percent (0% = dry, 100% = wet)
        try:
            percent = (1 - (raw - WET_ADC) / float(DRY_ADC - WET_ADC)) * 100.0
        except ZeroDivisionError:
            percent = 0.0
        if percent < 0:
            percent = 0.0
        if percent > 100:
            percent = 100.0
        return percent


def connect_wifi(ssid, password, timeout=15):
    try:
        import network
    except Exception:
        print('network module not available; skipping Wi-Fi')
        return False

    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if wlan.isconnected():
        print('Already connected to Wi-Fi')
        return True

    print('Connecting to Wi-Fi:', ssid)
    wlan.connect(ssid, password)
    start = time.time()
    while not wlan.isconnected() and (time.time() - start) < timeout:
        time.sleep(1)
    if wlan.isconnected():
        print('Connected, IP:', wlan.ifconfig()[0])
        return True
    print('Wi-Fi connect failed')
    return False


def send_telemetry(url, payload):
    if not url:
        return False
    if requests is None:
        return False
    try:
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        r.close()
        return True
    except Exception as e:
        print('Telemetry post failed:', e)
        return False


def main():
    sensor = MoistureSensor(ADC_PIN, DIGITAL_SENSOR_PIN, ma_window=MA_WINDOW)
    relay = Relay(RELAY_PIN, active_low=RELAY_ACTIVE_LOW)

    last_watering = 0
    watering = False
    watering_start = 0
    last_telemetry = 0
    low_count = 0
    boot_time = time.time()

    wifi_available = False
    if ENABLE_WIFI and WIFI_SSID and WIFI_PASSWORD:
        wifi_available = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    else:
        wifi_available = False

    print('Experiment 02 starting (local sensor + telemetry:', bool(wifi_available), ')')

    try:
        while True:
            # Read both the latest raw sample and the smoothed value.
            # Use the latest raw sample to detect sensor disconnects/saturation
            # (a single saturated sample should not be masked by smoothing).
            raw_smoothed = sensor.read_smoothed()
            raw_latest = sensor.read_raw()
            digital = sensor.digital.value() if sensor.digital else None

            now = time.time()

            # Reject implausible sensor reads (e.g. ADC floating / disconnected)
            if raw_latest >= SENSOR_RAW_DISCONNECTED or raw_latest <= SENSOR_RAW_DISCONNECTED_LOW:
                # sensor likely disconnected or floating to an extreme; do not start watering
                print('RAW:', raw_latest, 'DIGITAL:', digital, 'RELAY_ON:', relay.is_on())
                if raw_latest >= SENSOR_RAW_DISCONNECTED:
                    print('Sensor reading implausible (raw >= {}). Skipping start.'.format(SENSOR_RAW_DISCONNECTED))
                else:
                    print('Sensor reading implausible (raw <= {}). Skipping start.'.format(SENSOR_RAW_DISCONNECTED_LOW))
                # ensure relay is off for safety
                if relay.is_on():
                    relay.off()
                    watering = False
                    last_watering = now
                time.sleep(SAMPLE_INTERVAL)
                continue

            # ensure smoothed value is based on valid samples
            if raw_smoothed is None:
                print('No valid smoothed samples yet; waiting')
                time.sleep(SAMPLE_INTERVAL)
                continue

            # use smoothed value for decision-making and telemetry
            raw = raw_smoothed
            percent = sensor.read_percent(raw)

            # Telemetry (periodic)
            if wifi_available and TELEMETRY_URL and (now - last_telemetry) >= TELEMETRY_INTERVAL:
                payload = {'raw': raw, 'moisture_percent': round(percent,1), 'relay': relay.is_on(), 'ts': int(now)}
                ok = send_telemetry(TELEMETRY_URL, payload)
                print('Telemetry sent' if ok else 'Telemetry failed')
                last_telemetry = now

            print('RAW:', raw, 'MOIST%', round(percent,1), 'DIGITAL:', digital, 'RELAY_ON:', relay.is_on())

            # allow automatic starts only after boot delay
            elapsed_since_boot = now - boot_time

            if not watering:
                # allowed to start only if enough time passed since last watering and after boot delay
                if (now - last_watering) >= MIN_INTERVAL_BETWEEN_WATERING and elapsed_since_boot >= BOOT_DELAY_SECONDS:
                    # require several consecutive low readings to avoid false starts
                    # Determine whether digital pin currently signals wet
                    digital_is_wet = None
                    if sensor.digital is not None:
                        digital_is_wet = (digital == 1) if DIGITAL_WET_HIGH else (digital == 0)

                    # require digital to indicate dry (or be absent) to start watering
                    digital_allows_start = (sensor.digital is None) or (digital_is_wet is False)

                    if percent <= START_WATER_PERCENT and digital_allows_start:
                        low_count += 1
                        print('Consecutive low readings:', low_count)
                        if low_count >= REQUIRED_CONSECUTIVE:
                            print('Start watering: moisture <=', START_WATER_PERCENT)
                            relay.on()
                            watering = True
                            watering_start = now
                            low_count = 0
                    else:
                        # reset counter
                        low_count = 0
                else:
                    # not allowed to start yet; ensure counter reset
                    low_count = 0
            else:
                # Stop conditions: reached stop percent or max watering time
                # Stop if analog percent reached or digital sensor signals wet
                # stop if analog percent reached or digital sensor signals wet
                digital_is_wet = None
                if sensor.digital is not None:
                    digital_is_wet = (digital == 1) if DIGITAL_WET_HIGH else (digital == 0)

                if percent >= STOP_WATER_PERCENT or (sensor.digital is not None and digital_is_wet):
                    print('Stop watering: moisture >= {} or digital indicates wet'.format(STOP_WATER_PERCENT))
                    relay.off()
                    watering = False
                    last_watering = now
                elif (now - watering_start) >= MAX_WATERING_TIME:
                    print('Stop watering: max watering time reached')
                    relay.off()
                    watering = False
                    last_watering = now

            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print('Interrupted by user — shutting down')
        relay.off()
    except Exception as e:
        print('Unhandled error:', e)
        relay.off()


if __name__ == '__main__':
    main()
