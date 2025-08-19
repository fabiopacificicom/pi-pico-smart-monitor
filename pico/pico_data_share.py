# pico_data_share.py
# This module provides a function to send sensor data to the Pi over USB serial.
# Import and call send_status(temp, humi) from your main loop.

import sys

def send_status(temp, humi):
    """
    Send the current temperature and humidity to the Pi via USB serial as a CSV line.
    Example output: 25,60\n
    Args:
        temp (int or float): Temperature value
        humi (int or float): Humidity value
    """
    try:
        # Print to sys.stdout (USB serial)
        print("{},{:.1f}".format(temp, humi))
        sys.stdout.flush()
    except Exception as e:
        pass  # Optionally log or handle errors
