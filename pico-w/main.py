import network
import urequests
import time
from machine import Pin

# WiFi credentials
SSID = 'YOUR_WIFI_SSID'
PASSWORD = 'YOUR_WIFI_PASSWORD'

# Configuration
SENSOR_URL = 'http://192.168.1.120:5000/pico/sensors'  # Update with your Pi's IP if needed
POLL_INTERVAL = 1      # Check every 1 second for faster response to moisture changes
MAX_RETRIES = 3        # Number of retries for failed requests

# Watering safety limits (all times in seconds)
MAX_WATERING_TIME = 10     # Maximum time pump can run continuously
COOLDOWN_PERIOD = 300      # 5 minutes wait between watering cycles
SAFETY_CHECK_INTERVAL = 2   # Check moisture more frequently when pump is running

# Use GP15 as relay control pin (connect to relay IN)
relay = Pin(15, Pin.OUT)
relay.init(Pin.IN)  # Ensure relay is OFF (IN disconnected)

# Watering cycle tracking
last_watering_time = 0     # Track when we last watered
watering_start_time = 0    # Track when current watering cycle started
is_watering = False        # Track if we're currently watering

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to WiFi...')
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
print('Connected. IP:', wlan.ifconfig()[0])

def can_start_watering():
    """Check if it's safe to start a new watering cycle"""
    global last_watering_time
    current_time = time.time()
    
    # Check if enough time has passed since last watering
    if current_time - last_watering_time < COOLDOWN_PERIOD:
        remaining = COOLDOWN_PERIOD - (current_time - last_watering_time)
        print(f'Cooling down. {remaining}s remaining before next watering cycle')
        return False
    return True

def check_watering_duration():
    """Check if current watering cycle has exceeded maximum duration"""
    global watering_start_time, is_watering
    if not is_watering:
        return
    
    current_time = time.time()
    duration = current_time - watering_start_time
    
    if duration >= MAX_WATERING_TIME:
        print(f'Maximum watering time ({MAX_WATERING_TIME}s) reached!')
        control_relay(False, "maximum duration reached")
        is_watering = False
        last_watering_time = current_time

def control_relay(state, reason=""):
    """Control relay with proper status message and timing tracking"""
    global is_watering, watering_start_time, last_watering_time
    
    if state:  # Turn ON
        if not is_watering and can_start_watering():
            relay.init(Pin.OUT)
            relay.value(0)  # Active LOW
            print(f'Relay ON: {reason}')
            is_watering = True
            watering_start_time = time.time()
        else:
            print('Skipping watering: cooling down')
    else:  # Turn OFF
        if is_watering:
            last_watering_time = time.time()
        relay.init(Pin.IN)
        is_watering = False
        print(f'Relay OFF: {reason}')

while True:
    # Always check watering duration first
    check_watering_duration()
    
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            print('Fetching sensor data...')
            response = urequests.get(SENSOR_URL)
            data = response.json()
            print('Sensor data:', data)
            
            if 'moisture' in data:
                moisture = data['moisture']
                print('Moisture value:', moisture)
                
                if moisture == 0 and not is_watering:
                    control_relay(True, "soil is dry")
                elif moisture == 1:
                    control_relay(False, "soil is wet")
                break  # Success, exit retry loop
                
            else:
                control_relay(False, "moisture value not found")
                
        except Exception as e:
            retry_count += 1
            print(f'Error fetching data (attempt {retry_count}/{MAX_RETRIES}):', e)
            if retry_count == MAX_RETRIES:
                control_relay(False, "max retries reached")
        finally:
            try:
                response.close()
            except:
                pass
    
    # Use different polling intervals based on state
    if is_watering:
        time.sleep(SAFETY_CHECK_INTERVAL)  # Check more frequently while watering
    else:
        time.sleep(POLL_INTERVAL)  # Normal interval when not watering