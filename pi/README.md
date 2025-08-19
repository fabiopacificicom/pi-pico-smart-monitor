# Pi Webcam Streaming Server

This folder contains a simple Flask-based server for streaming video from a Raspberry Pi webcam.

## Requirements

- Python 3.x
- Flask
- OpenCV (`cv2`)

Install dependencies with:

```
pip install flask opencv-python
```


## Available Routes

### `/`

- **Method:** GET
- **Description:**
  - Serves a simple HTML page styled with Tailwind CSS.
  - Displays the live webcam stream in an `<img>` tag.
  - Shows a title and a short description.

### `/video_feed`

- **Method:** GET
- **Description:**
  - Streams live video from the Raspberry Pi webcam using MJPEG format.
  - The route yields JPEG frames from the webcam in a multipart HTTP response.
  - Used as the source for the `<img src="/video_feed">` tag on the main page.

### `/pico/sensors`

- **Method:** GET
- **Description:**
  - Returns the latest sensor data (temperature, humidity) received from the Pico over USB serial as JSON.
  - Example response: `{ "temp": 25.0, "humi": 60.0 }`
  - Data is updated in real time as the Pico sends new readings.

## How It Works

- The server opens the default webcam (`/dev/video0` or camera index 0) using OpenCV.
- Frames are read, encoded as JPEG, and streamed to clients.
- The main page (`/`) embeds the video stream from `/video_feed`.

## Usage

Run the server with:

```
python main.py
```

Then open your browser and go to `http://<raspberry-pi-ip>:5000/` to view the webcam stream.

---

**Note:**

- Make sure your webcam is connected and accessible by the Pi.
- The server listens on all interfaces (`0.0.0.0`) by default.
