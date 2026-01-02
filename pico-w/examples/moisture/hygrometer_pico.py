"""
MicroPython example for Raspberry Pi Pico W.

Wiring (Pico W):
  - D0 (module) -> GP18 (physical pin 24 on Pico header, use correct pin mapping for your board)
  - GND -> GND
  - VCC -> 3V3

Notes:
  - The sensor module provides a digital output on D0. The module behavior in
    the original doc prints "HIGH" when `input == 0`, so this script follows
    the same logic (D0==0 => "HIGH moisture"). If your module behaves
    differently, invert the condition.
  - Run this on the Pico W using Thonny or by copying the file to the device
    as `main.py` / `hygrometer.py` and monitor the REPL/serial output.
"""

import time
from machine import Pin, ADC

# Wiring (Pico W):
#  - Module A0 (analog out) -> GP26 (ADC0)  (recommended for percentage readings)
#  - Module D0 (digital out) -> GP18 (optional, comparator output)
#  - GND -> GND
#  - VCC -> 3V3

# Pin definitions (change if you wire differently)
ADC_PIN = 26     # GP26 / ADC0
DIGIOUT_PIN = 18 # optional digital comparator output

# Sampling and smoothing
SAMPLE_INTERVAL = 0.5   # seconds between samples
MA_WINDOW = 8           # moving-average window size

# Calibration / mapping
# If AUTO_CALIBRATE is True the script will sample for a few seconds at
# startup (assumes sensor is in air = dry) and set `dry_raw` to that value.
# Set `wet_raw` manually if you know an approximate wet reading, or keep the
# default and refine after testing.
AUTO_CALIBRATE = True
CALIB_SAMPLES = 16
wet_raw = 20000   # default estimate for a very wet soil; adjust after testing

# Optional inversion: if your readings increase with moisture set INVERT=True
INVERT = False

adc = ADC(ADC_PIN)
dig = Pin(DIGIOUT_PIN, Pin.IN)

def read_adc_u16():
  # return raw 0..65535
  try:
    return adc.read_u16()
  except Exception as e:
    print('ADC read error:', e)
    return None

def moving_average(buf, value, size):
  buf.append(value)
  if len(buf) > size:
    buf.pop(0)
  return sum(buf) // len(buf)

def raw_to_percent(raw, dry, wet, invert=False):
  # Map raw value to 0..100% where 0=dry, 100=wet
  if dry == wet:
    return 0
  if invert:
    # invert mapping when needed
    raw = 65535 - raw
    dry = 65535 - dry
    wet = 65535 - wet

  # Clamp raw between wet and dry
  if raw >= dry:
    return 0
  if raw <= wet:
    return 100
  # linear interpolation
  try:
    pct = (dry - raw) * 100 // (dry - wet)
  except ZeroDivisionError:
    pct = 0
  if pct < 0:
    pct = 0
  if pct > 100:
    pct = 100
  return int(pct)

def print_help(dry, wet):
  print('\n--- Moisture ADC test (Pico W) ---')
  print('ADC pin: GP{}'.format(ADC_PIN))
  print('Digital pin (D0 comparator): GP{}'.format(DIGIOUT_PIN))
  print('Calibration: dry_raw = {}, wet_raw = {}'.format(dry, wet))
  print('Move the potentiometer to adjust sensitivity, then record readings.')
  print('Press Ctrl+C to stop.\n')

time.sleep(1)

# Initial calibration: sample in-air (dry) if requested
dry_raw = None
if AUTO_CALIBRATE:
  print('Auto-calibrating dry baseline: keep sensor in air for a few seconds...')
  samples = []
  for _ in range(CALIB_SAMPLES):
    v = read_adc_u16()
    if v is not None:
      samples.append(v)
    time.sleep(0.1)
  if samples:
    dry_raw = sum(samples) // len(samples)
    print('Captured dry baseline (avg):', dry_raw)
  else:
    print('Calibration failed, no ADC samples read')

# Fallbacks
if dry_raw is None:
  # conservative defaults: assume dry ~ 60000, wet ~ 20000
  dry_raw = 60000
  print('Using fallback dry_raw =', dry_raw)

print_help(dry_raw, wet_raw)

buf = []
min_seen = 65535
max_seen = 0

try:
  while True:
    raw = read_adc_u16()
    if raw is None:
      time.sleep(SAMPLE_INTERVAL)
      continue

    ma = moving_average(buf, raw, MA_WINDOW)

    # update seen ranges
    if ma < min_seen:
      min_seen = ma
    if ma > max_seen:
      max_seen = ma

    pct = raw_to_percent(ma, dry_raw, wet_raw, INVERT)

    # read digital comparator too (optional)
    try:
      d = dig.value()
    except Exception:
      d = None

    line = 'ADC raw={:5d}  MA={:5d}  %={:3d}'.format(raw, ma, pct)
    if d is not None:
      line += '  D0={}'.format(d)
    line += '  range(min/max)={}/{}'.format(min_seen, max_seen)
    print(line)

    time.sleep(SAMPLE_INTERVAL)
except KeyboardInterrupt:
  print('\nScript end!')

