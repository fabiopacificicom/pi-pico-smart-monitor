# Pi Pico W: WiFi Moisture Sensor Data Fetch Example
# This script connects to WiFi, fetches moisture data from a REST endpoint (served by the Pi), and prints the value.
# You can later use this value to control the relay/pump.

import network
import urequests
import time

# WiFi credentials
SSID = 'YOUR_WIFI_SSID'
PASSWORD = 'YOUR_WIFI_PASSWORD'


# REST endpoint URL for Pi sensor data
SENSOR_URL = 'http://192.168.1.120:5000/pico/sensors'  # Update with your Pi's IP if needed

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
        # Print the full JSON for debugging
        print('Sensor data:', data)
        # Try to print moisture value if present
        if 'moisture' in data:
            print('Moisture value:', data['moisture'])
        else:
            print('Moisture value not found in response.')
        response.close()
    except Exception as e:
        print('Error fetching data:', e)
    time.sleep(10)
