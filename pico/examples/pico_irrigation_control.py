# Pi Pico W: Relay and Water Pump Control Example
#
# Connections:
# - Relay IN: Pico GPIO 28
# - IR Sensor S: Pico GPIO 21
# - See pico_irrigation_control_plan.md for full wiring

from machine import Pin
import time

# Pin assignments
RELAY_PIN = 28      # GPIO for relay control
IR_SENSOR_PIN = 21  # GPIO for IR sensor

# Setup pins
relay = Pin(RELAY_PIN, Pin.OUT)
ir_sensor = Pin(IR_SENSOR_PIN, Pin.IN)


# Simulate soil moisture (True = dry, False = wet)
soil_is_dry = True  # Start with dry soil (pump ON)

# IR sensor logic: when button is pressed, IR sensor value changes (usually from 1 to 0 or vice versa)
last_ir_value = ir_sensor.value()
print("Press the OK button on the IR remote to stop the pump.")


try:
    while True:
        ir_value = ir_sensor.value()
        print(f"[DEBUG] IR sensor state: {ir_value}, Last IR: {last_ir_value}, Soil dry: {soil_is_dry}")

        # If soil is dry, pump should be ON unless IR button is pressed
        # ACTIVE-LOW RELAY: 0 = ON, 1 = OFF
        if soil_is_dry:
            relay.value(0)  # 0 = ON for active-low relay
            print("[DEBUG] Soil is dry: Pump ON (relay.value=0, active-low)")
        else:
            relay.value(1)  # 1 = OFF for active-low relay
            print("[DEBUG] Soil is wet: Pump OFF (relay.value=1, active-low)")

        # Detect IR button press (falling edge: 1 -> 0 or rising edge: 0 -> 1)
        if ir_value != last_ir_value:
            print(f"[DEBUG] IR sensor changed! Previous: {last_ir_value}, Now: {ir_value}")
            # Button press detected (change in IR sensor state)
            if ir_value == 0:
                print("[DEBUG] IR OK button pressed! Setting soil_is_dry = False (Pump OFF)")
                soil_is_dry = False  # Set to wet, turn off pump
            else:
                print("[DEBUG] IR sensor changed but not to 0 (no action)")
        last_ir_value = ir_value

        time.sleep(0.2)
except KeyboardInterrupt:
    relay.value(0)
    print("Stopped. Pump OFF.")
