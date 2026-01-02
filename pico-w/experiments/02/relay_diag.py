"""Relay diagnostic for Experiment 02

Simple script to toggle the relay so you can verify wiring and pump control.
Run on the Pico and observe:
- You should hear the relay click on each activation.
- With a multimeter measure COM-NO continuity when relay is ON.
- Only connect the pump after verifying relay toggles and wiring is correct.

Usage:
from relay_diag import main
main()

"""

import time
from machine import Pin

RELAY_PIN = 15
RELAY_ACTIVE_LOW = True
PULSE_COUNT = 6
# Short on-time to reduce chance of relay left energized if script is killed
PULSE_ON = 0.2
PULSE_OFF = 0.5

class Relay:
    def __init__(self, pin_no, active_low=True):
        self.pin = Pin(pin_no, Pin.OUT)
        self.active_low = active_low
        self.off()

    def on(self):
        self.pin.value(0 if self.active_low else 1)

    def off(self):
        self.pin.value(1 if self.active_low else 0)

    def is_on(self):
        val = self.pin.value()
        return (val == 0) if self.active_low else (val == 1)


def main():
    # Minimal interactive toggler:
    # - call `on()`, `off()`, `toggle()` from REPL for manual control
    # - or run this script and press Enter to toggle, 'q' then Enter to quit
    r = Relay(RELAY_PIN, active_low=RELAY_ACTIVE_LOW)
    print('Relay diag interactive. RELAY_PIN={}, active_low={}'.format(RELAY_PIN, RELAY_ACTIVE_LOW))
    print("Commands: <Enter> toggle, 'o'+Enter ON, 'f'+Enter OFF, 'q'+Enter quit")
    try:
        while True:
            cmd = input('> ')
            if not cmd:
                # toggle
                if r.is_on():
                    r.off()
                else:
                    r.on()
            elif cmd.lower().startswith('o'):
                r.on()
            elif cmd.lower().startswith('f'):
                r.off()
            elif cmd.lower().startswith('q'):
                break
            print('pin value:', r.pin.value(), 'relay_on:', r.is_on())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Error:', e)
    finally:
        r.off()
        print('Exiting; relay OFF')


# Convenience functions for REPL control
_relay = Relay(RELAY_PIN, active_low=RELAY_ACTIVE_LOW)

def on():
    _relay.on()

def off():
    _relay.off()

def toggle():
    if _relay.is_on():
        _relay.off()
    else:
        _relay.on()

def status():
    return {'pin': _relay.pin.value(), 'on': _relay.is_on()}

if __name__ == '__main__':
    main()
