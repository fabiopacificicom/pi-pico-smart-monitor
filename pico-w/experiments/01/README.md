# Watering system experiment 01

## Overview

This experiment implements a simple automated watering controller using a Pico W that polls an external sensor API and controls a relay driving a pump. The controller's goal is to start watering when the soil is detected as dry and stop when the soil is wet while enforcing safety limits to prevent over-watering.

Key responsibilities implemented in `01-main.py`:

- Connect to Wi‑Fi and poll a remote sensor endpoint (`SENSOR_URL`).
- Turn a relay (GP15) on/off to control a pump (relay is active LOW).
- Apply safety limits: `MAX_WATERING_TIME`, `COOLDOWN_PERIOD` and frequent checks while watering.
- Retry failed HTTP requests up to `MAX_RETRIES` and disable watering if failures persist.

## Hardware

- Raspberry Pi Pico W (controller)
- Relay module controlled by GP15 (relay active LOW; wiring must ensure correct input state when OFF)
- Moisture sensor connected to a separate microcontroller or the Pi (exposes an HTTP endpoint consumed by this script)

## Software / Logic Summary

- The Pico W polls the configured `SENSOR_URL` every `POLL_INTERVAL` seconds when idle.
- If the returned JSON contains `moisture`, the code interprets `0` as dry and `1` as wet.
- When dry and safety checks pass, the relay is initialized as an output and set LOW to energize the pump.
- While watering, the program checks watering duration more frequently (`SAFETY_CHECK_INTERVAL`) and will forcibly stop the pump if `MAX_WATERING_TIME` is reached.
- After watering the system records `last_watering_time` and will refuse to start another cycle until `COOLDOWN_PERIOD` has elapsed.
- On repeated network failures the code stops the pump and prevents attempts to water until conditions improve.

## Observations (from run / code review)

- The controller relies on an external HTTP endpoint for moisture readings; this introduces latency and a potential synchronization gap between the physical sensor state and when the Pico acts.
- The code contains useful safety guards (`MAX_WATERING_TIME`, `COOLDOWN_PERIOD`, retry logic) which mitigate risk of overwatering even when sensor data is delayed or missing.
- The relay is toggled by re-initializing the pin between `Pin.OUT` and `Pin.IN`. This works practically to set the line to high-impedance for OFF, but it may be clearer to explicitly set `relay.value(1)` for OFF (if hardware supports it) or document why `Pin.IN` is preferred for your relay module.
- Using a boolean `moisture` flag (0/1) is simple but leaves no headroom for thresholding or smoothing noisy analog readings.

## Root Cause of the Experiment Issues

- Primary issue: sensor synchronization and reliance on an HTTP endpoint introduced delays and occasional missing/incorrect readings. When a network call fails or returns stale values, the controller either skips watering or may leave the pump running until the safety timeout.
- Secondary issue: wiring/behavior assumptions of the relay (active LOW) and toggling via `Pin.IN` can lead to an ambiguous OFF state on some hardware.

## Conclusions & Lessons Learned

- Local, low-latency access to raw sensor readings reduces the risk of synchronization problems. Where possible, connect the moisture sensor directly to the same microcontroller that controls the relay (or use a low-latency messaging channel).
- Safety features in the controller are essential: keep `MAX_WATERING_TIME` and `COOLDOWN_PERIOD` to prevent overwatering even in failure modes.
- Add signal validation and smoothing (e.g., require multiple dry samples before starting, or implement hysteresis) to avoid rapid on/off cycling due to noisy sensors.
- Document and standardize the relay wiring and active polarity. Prefer explicit OFF/ON values over reinitializing the pin mode when possible for clarity.

## Recommendations / Next Steps

- Where feasible, wire the moisture sensor to the Pico W directly (ADC input) and implement a small moving-average or debounce before acting.
- If the sensor must remain remote, consider running a local MQTT broker or WebSocket stream to reduce polling latency and handle transient network failures more gracefully.
- Replace the simple 0/1 moisture model with a numeric reading and configurable threshold(s). Example: start watering when moisture < 300 and stop when > 600 (ADC units).
- Improve relay handling: set explicit output values for ON/OFF, and add a small hardware pull-up/pull-down if your relay input is floating when disconnected.
- Add logging of events (start/stop times, reasons) to persistent storage or a remote log to help diagnose intermittent issues.

## Configuration & How to Run

- Edit `01-main.py` to set `SSID`, `PASSWORD`, and `SENSOR_URL` to match your network and sensor endpoint.
- Verify `MAX_WATERING_TIME`, `COOLDOWN_PERIOD`, and `POLL_INTERVAL` suit your plants and pump.
- Deploy the script to the Pico W and monitor serial output for messages like `Relay ON:` and `Relay OFF:` to see decision reasons.

## Example Troubleshooting Checklist

- If the pump never starts: verify `SENSOR_URL` JSON contains `moisture` and that the device returns `0` when dry.
- If pump doesn't stop: confirm `moisture` value returns `1` when wet, ensure `MAX_WATERING_TIME` is set and the relay OFF behavior actually disables the pump.
- If network errors occur frequently: decrease `POLL_INTERVAL` to limit load, add exponential backoff, or move to a push-based sensor update model.

---

If you want, I can also update `01-main.py` to read a local ADC moisture sensor, add hysteresis, or change relay handling to explicit ON/OFF values — tell me which improvement you prefer.
