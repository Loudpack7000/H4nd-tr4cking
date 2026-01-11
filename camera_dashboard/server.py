import io
import time
import threading
import os
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

# Try to import picamera2, fallback to OpenCV if not on a Pi
try:
    import picamera2
    HAS_PICAMERA = True
except ImportError:
    import cv2
    HAS_PICAMERA = False

app = FastAPI()

class CameraStreamer:
    def __init__(self):
        self.stopped = False
        self.latest_frame = None
        self.fps_actual = 0
        self.lock = threading.Lock()
        self._frame_count = 0
        self._last_time = time.time()
        
        if HAS_PICAMERA:
            self.picam2 = picamera2.Picamera2()
            self.config = self.picam2.create_video_configuration(
                main={"size": (1280, 720), "format": "YUV420"}
            )
            self.picam2.configure(self.config)
            self.picam2.set_controls({"FrameDurationLimits": (16666, 16666)})
        else:
            # Laptop webcam fallback
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def start(self):
        if HAS_PICAMERA:
            self.picam2.start()
        
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print(f"Camera capture loop started (Using {'PiCamera2' if HAS_PICAMERA else 'OpenCV'})")

    def _capture_loop(self):
        while not self.stopped:
            try:
                if HAS_PICAMERA:
                    buf = io.BytesIO()
                    self.picam2.capture_file(buf, format="jpeg")
                    frame_data = buf.getvalue()
                else:
                    success, frame = self.cap.read()
                    if not success:
                        time.sleep(0.1)
                        continue
                    # Encode to JPEG for the stream
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_data = buffer.tobytes()
                
                with self.lock:
                    self.latest_frame = frame_data
                    self._frame_count += 1
                    
                now = time.time()
                if now - self._last_time >= 1.0:
                    self.fps_actual = self._frame_count / (now - self._last_time)
                    self._frame_count = 0
                    self._last_time = now
                
                time.sleep(0.001)
            except Exception as e:
                time.sleep(0.1)

    def get_frame(self):
        with self.lock:
            return self.latest_frame

    def stop(self):
        self.stopped = True
        if HAS_PICAMERA:
            self.picam2.stop()
            self.picam2.close()
        else:
            self.cap.release()

streamer = CameraStreamer()

@app.on_event("startup")
async def startup_event():
    streamer.start()

@app.on_event("shutdown")
async def shutdown_event():
    streamer.stop()

def gen_frames():
    while True:
        frame = streamer.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(1/100)

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
async def get_stats():
    return {
        "fps": round(streamer.fps_actual, 2),
        "resolution": "1280x720",
        "camera": "PiCamera" if HAS_PICAMERA else "Webcam"
    }

# Use relative path for portability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
