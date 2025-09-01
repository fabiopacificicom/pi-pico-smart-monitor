# Pi Pico W Irrigation Control: Plan

## Hardware Connections

- Relay VCC (5V) → Pico VBUS
- Relay GND → Pico GND
- Relay IN → Pico GPIO 28
- Relay NO → Water Pump -
- Relay NC → Water Pump +
- Relay COM → Pico GND
- IR Sensor + → Pico 3V
- IR Sensor - → Pico GND
- IR Sensor S → Pico GPIO 21

## Tasks

1. **Write MicroPython script for Pico W:**
   - Initialize GPIO 28 as output (relay control)
   - Initialize GPIO 21 as input (IR sensor)
   - Simulate soil moisture (hardcoded variable)
   - When "soil is dry":
     - Activate relay (turn on pump)
     - Optionally, check IR sensor and log state
   - When "soil is wet":
     - Deactivate relay (turn off pump)
2. **Test relay and pump activation**
   - Confirm relay clicks and pump runs when triggered
3. **Print/log IR sensor state**
   - Print IR sensor value to REPL for debugging
4. **Make script modular**
   - Easy to swap hardcoded value for real sensor or remote input later
5. **Document pin assignments and usage in code comments**

---

Next: Add the MicroPython script in `pico/examples/` to control relay and pump.
