import network
import urequests
import time
from machine import Pin

# WiFi credentials
SSID = 'YOUR_WIFI_SSID'
PASSWORD = 'YOUR_WIFI_PASSWORD'

# REST endpoint URL for Pi sensor data
SENSOR_URL = 'http://192.168.1.120:5000/pico/sensors'  # Update with your Pi's IP if needed

# Use GP15 as relay control pin (connect to relay IN)
relay = Pin(15, Pin.OUT)
relay.init(Pin.IN)  # Ensure relay is OFF (IN disconnected)

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to WiFi...')
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
print('Connected. IP:', wlan.ifconfig()[0])

while True:
    try:
        print('Fetching sensor data...')
        response = urequests.get(SENSOR_URL)
        data = response.json()
        print('Sensor data:', data)
        if 'moisture' in data:
            moisture = data['moisture']
            print('Moisture value:', moisture)
            if moisture == 0:
                relay.init(Pin.OUT)
                relay.value(0)  # ON (IN to GND)
                print('Relay ON (soil is dry)')
            else:
                relay.init(Pin.IN)  # OFF (IN disconnected)
                print('Relay OFF (soil is wet)')
        else:
            relay.init(Pin.IN)
            print('Moisture value not found, relay OFF for safety.')
        response.close()
    except Exception as e:
        relay.init(Pin.IN)
        print('Error fetching data, relay OFF for safety:', e)
    time.sleep(10)