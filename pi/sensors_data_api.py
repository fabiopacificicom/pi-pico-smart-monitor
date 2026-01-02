# sensors_data_api.py
# Flask blueprint to expose Pico sensor data via HTTP endpoint

from flask import Blueprint, jsonify, request
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

@sensors_api.route('/pico/sensors', methods=['GET', 'POST'])
def pico_sensors():
    if request.method == 'POST':
        try:
            payload = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'invalid json'}), 400

        # Update temp/humi if present
        if 'temp' in payload:
            try:
                sensor_data['temp'] = float(payload['temp'])
            except Exception:
                pass
        if 'humi' in payload:
            try:
                sensor_data['humi'] = float(payload['humi'])
            except Exception:
                pass

        # Accept explicit moisture (0/1)
        if 'moisture' in payload:
            try:
                sensor_data['moisture'] = int(payload['moisture'])
            except Exception:
                pass
        # Or accept moisture_percent and map to 0/1 using a 50% threshold
        elif 'moisture_percent' in payload:
            try:
                mp = float(payload['moisture_percent'])
                sensor_data['moisture'] = 0 if mp <= 50.0 else 1
                # also store the raw percent for richer UI if desired
                sensor_data['moisture_percent'] = round(mp, 1)
            except Exception:
                pass

        return jsonify({'status': 'ok'}), 200

    # GET returns latest sensor data (unchanged behavior)
    return jsonify(sensor_data)

# Start the serial reader thread when this module is imported
threading.Thread(target=serial_reader, daemon=True).start()
