# sensors_data_api.py
# Flask blueprint to expose Pico sensor data via HTTP endpoint

from flask import Blueprint, jsonify
import serial
import threading

sensors_api = Blueprint('sensors_api', __name__)

sensor_data = {'temp': None, 'humi': None, 'moisture': None}
SERIAL_PORT = '/dev/ttyACM0'  # Update if your Pico appears as a different device
BAUDRATE = 115200

# Serial reader thread

def serial_reader():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        while True:
            line = ser.readline().decode().strip()
            if line:
                try:
                    parts = line.split(',')
                    if len(parts) == 3:
                        temp, humi, moisture = parts
                        sensor_data['temp'] = float(temp)
                        sensor_data['humi'] = float(humi)
                        sensor_data['moisture'] = int(moisture)
                    elif len(parts) == 2:
                        temp, humi = parts
                        sensor_data['temp'] = float(temp)
                        sensor_data['humi'] = float(humi)
                        sensor_data['moisture'] = None
                except Exception:
                    continue
    except Exception as e:
        print(f"Serial error: {e}")

@sensors_api.route('/pico/sensors')
def pico_sensors():
    return jsonify(sensor_data)

# Start the serial reader thread when this module is imported
threading.Thread(target=serial_reader, daemon=True).start()
