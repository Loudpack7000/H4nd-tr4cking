import io
import time
import threading
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import picamera2

app = FastAPI()

class CameraStreamer:
    def __init__(self):
        self.picam2 = picamera2.Picamera2()
        
        # Configure for high quality
        # 1280x720 is a good "High Quality" balance for web streaming
        self.config = self.picam2.create_video_configuration(
            main={"size": (1280, 720), "format": "YUV420"}
        )
        self.picam2.configure(self.config)
        
        # Set controls for 60fps
        # 16666us = 1/60s
        self.picam2.set_controls({"FrameDurationLimits": (16666, 16666)})
        
        self.latest_frame = None
        self.fps_actual = 0
        self.lock = threading.Lock()
        self._frame_count = 0
        self._last_time = time.time()
        self.stopped = False

    def start(self):
        self.picam2.start()
        # We'll run a background thread that constantly captures JPEGs
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print("Camera capture loop started")

    def _capture_loop(self):
        while not self.stopped:
            try:
                # This uses the hardware encoder to generate a JPEG
                # It's very fast and low CPU
                buf = io.BytesIO()
                self.picam2.capture_file(buf, format="jpeg")
                
                with self.lock:
                    self.latest_frame = buf.getvalue()
                    self._frame_count += 1
                    
                now = time.time()
                if now - self._last_time >= 1.0:
                    self.fps_actual = self._frame_count / (now - self._last_time)
                    self._frame_count = 0
                    self._last_time = now
                
                # Tiny sleep to allow context switching
                time.sleep(0.001)
            except Exception as e:
                # print(f"Capture error: {e}")
                time.sleep(0.1)

    def get_frame(self):
        with self.lock:
            return self.latest_frame

    def stop(self):
        self.stopped = True
        self.picam2.stop()
        self.picam2.close()

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
        # This controls the transmission rate to the browser
        time.sleep(1/100) # 100fps max relay

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
async def get_stats():
    return {
        "fps": round(streamer.fps_actual, 2),
        "resolution": "1280x720",
        "camera": "IMX708"
    }

# Absolute path for clarity
STATIC_DIR = "/home/loud/Desktop/Field/camera_dashboard/static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use log_level="warning" to keep the console clean
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
