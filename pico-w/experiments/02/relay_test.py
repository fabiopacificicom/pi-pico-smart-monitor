"""Simple relay test helper for Experiment 02.

Upload this file as `main.py` (or run via REPL) to manually toggle the relay
without running the full moisture-control logic.
"""

from machine import Pin

RELAY_PIN = 15
RELAY_ACTIVE_LOW = False  # set to False if your relay energizes on HIGH

_pin = Pin(RELAY_PIN, Pin.OUT)


def relay_on():
    """Energize the relay/pump."""
    _pin.value(0 if RELAY_ACTIVE_LOW else 1)


def relay_off():
    """De-energize the relay/pump."""
    _pin.value(1 if RELAY_ACTIVE_LOW else 0)


def is_on():
    """Return True if the relay input is asserted."""
    val = _pin.value()
    return (val == 0) if RELAY_ACTIVE_LOW else (val == 1)


relay_off()
print('Relay test ready — use relay_on(), relay_off(), is_on() in the REPL.')
