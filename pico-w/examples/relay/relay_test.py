import machine
import utime

# Use GP15 as relay control pin (connect to relay IN)
relay = machine.Pin(15, machine.Pin.OUT)

while True:
    relay.value(0)  # ON (IN to GND)
    print('Relay ON (IN to GND)')
    utime.sleep(3)
    relay.init(machine.Pin.IN)  # Set pin to input (disconnects IN)
    print('Relay OFF (IN disconnected)')
    utime.sleep(3)
    relay.init(machine.Pin.OUT)  # Set back to output for next loop