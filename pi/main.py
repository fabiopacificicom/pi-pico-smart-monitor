
# Simple webcam streaming server using Flask and OpenCV
from flask import Flask, Response, render_template_string
from prototype_leaf_detection import plant_health_api
import cv2

app = Flask(__name__)


from sensors_data_api import sensors_api
# Register sensors API blueprint
app.register_blueprint(sensors_api)

# Register plant health check blueprint
app.register_blueprint(plant_health_api)

def gen_frames():
	cap = cv2.VideoCapture(0)
	if not cap.isOpened():
		raise RuntimeError("Could not open webcam.")
	while True:
		success, frame = cap.read()
		if not success:
			break
		ret, buffer = cv2.imencode('.jpg', frame)
		frame = buffer.tobytes()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
	# Simple HTML page to show the video stream
	return render_template_string('''
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Webcam Stream</title>
		<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
	</head>
	<body class="bg-gray-900 min-h-screen flex flex-col items-center justify-center">
		<div class="bg-white rounded-lg shadow-lg p-8 mt-8 flex flex-col items-center">
			<h1 class="text-3xl font-bold mb-6 text-gray-800">Webcam Stream</h1>
			<div class="border-4 border-gray-300 rounded-lg overflow-hidden mb-4">
				<img src="/video_feed" width="640" height="480" class="block" />
			</div>
			<p class="text-gray-600">Live video from your Raspberry Pi webcam.</p>
		</div>
		<footer class="mt-8 text-gray-400 text-sm">&copy; 2025 PiCam</footer>
	</body>
	</html>
	''')

@app.route('/video_feed')
def video_feed():
	return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=False)

