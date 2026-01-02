# Experiment 02 — Wiring and Safety notes

This file documents the recommended wiring for the Pico W, the relay module, and a 5V pump (powered from VBUS ) used in `experiments/02/02-main.py`.

Overview

- Relay module terminals (typical cheap 1‑channel board):
  - Side A (switch): `COM`, `NO`, `NC` (these are the switched contacts)
  - Side B (module power/control): `VCC`, `GND`, `IN` (and sometimes `JD-VCC` + jumper)

Goal

- Wire the pump so it is OFF by default and only powered when the relay is energized (COM → NO closed).

Wiring table (concise)

- Relay `VCC`  -> PICO-W VBUS
- Relay `GND`  -> PICO-W GND
- Pico `GP15`  -> Relay `IN` (control pin used by `02-main.py`)
- Pico-W VBUS  -> Relay `COM` (relay common contact)
- Pump +       -> Relay `NO` (normally open contact)
- Pump -       -> PICO-W GND
- Sensor `VCC` -> Pico 3.3V
- Sensor `GND` -> Pico GND
- Sensor `AO`  -> Pico GP26 (ADC0 / AO)
- Sensor `DO`  -> Pico GP18 (digital out, optional)
 
Implementation notes
--------------------

This experiment runs a MicroPython script `02-main.py` that reads a moisture
sensor on `GP26` and controls a relay on `GP15` to power a 5V pump from
`VBUS`. Telemetry support exists but is disabled by default so the script runs
locally without any credentials.

For quick hardware checks, use `relay_test.py` (same folder) to toggle the
relay manually via the REPL before running the full control logic.

Configuration and deployment

- Copy `02-main.py` to the device (rename to `main.py` or run it directly).
  Use Thonny or `mpremote`/`ampy` to upload files.
- Telemetry and Wi‑Fi are disabled (`ENABLE_WIFI = False`). If you want to send
  telemetry later, edit the constants in `02-main.py` manually and provide
  credentials there.
- Optional: upload `relay_test.py` first to verify relay polarity and wiring
  without powering the pump.

Safety notes and power

- The relay coil and pump are powered from the Pico W `VBUS` (USB 5V) in the
  wiring above. Be careful: many small pumps draw significant current on
  startup (stall current) and can exceed a USB port's current limit.
- If the pump current is unknown or >500mA, use a separate 5V power supply for
  the pump and the relay coil. When using a separate supply, ensure a common
  ground between the Pico and the pump supply.
- If your relay module exposes `JD-VCC` and a jumper, remove the jumper and
  power the coil from the external 5V supply for isolation if needed.
- Always test the wiring without the pump connected (use a multimeter or a
  small test load) before connecting the pump.

Validation & testing checklist

1. **Relay test** — Upload `relay_test.py`, call `relay_on()` / `relay_off()` in
  the REPL, and confirm pump stays OFF by default.
2. **ADC calibration** — In REPL, run `from machine import ADC, Pin; adc=ADC(Pin(26))`
  and sample `adc.read_u16()` for dry vs wet soil; update `DRY_ADC`/`WET_ADC` in
  `02-main.py` accordingly.
3. **Threshold verification** — With the full script running, confirm watering
  starts only when moisture <= 30% (or your configured start value) and stops
  when >= 60% (or when the digital DO pin reports wet).
4. **Safety timers** — Temporarily lower `MAX_WATERING_TIME` / increase
  `SAMPLE_INTERVAL` to ensure the timer shuts the relay off after the limit.
5. **Telemetry (optional)** — If you later enable Wi‑Fi, confirm connectivity
  and that telemetry POSTs succeed.

## Notes

- The provided `02-main.py` uses moving-average smoothing and hysteresis to
  avoid relay chatter.
- Review pump datasheet and confirm the USB port can supply the required
  current. When in doubt, use a separate supply.
