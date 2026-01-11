import subprocess
import time
import re

def test_fps_rpicam(width, height, requested_fps, frames=500):
    print(f"Testing {width}x{height} at {requested_fps} FPS using rpicam-vid...")
    
    cmd = [
        "rpicam-vid",
        "--frames", str(frames),
        "--nopreview",
        "--width", str(width),
        "--height", str(height),
        "--framerate", str(requested_fps),
        "--codec", "mjpeg",
        "--denoise", "cdn_off",
        "--awb", "indoor",
        "--shutter", "2000", # 2ms exposure to ensure it doesn't limit FPS
        "-o", "output_test.mjpeg"
    ]
    
    start_time = time.time()
    try:
        # Run rpicam-vid
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        if result.returncode != 0:
            print(f"Error running rpicam-vid: {result.stderr}")
            return None
        
        actual_duration = end_time - start_time
        actual_fps = frames / actual_duration
        
        print(f"Results for {width}x{height}:")
        print(f"  Requested FPS: {requested_fps}")
        print(f"  Actual FPS:    {actual_fps:.2f}")
        print(f"  Duration for {frames} frames: {actual_duration:.2f}s")
        print("-" * 30)
        return actual_fps
    except Exception as e:
        print(f"Failed to test: {e}")
        return None

if __name__ == "__main__":
    modes = [
        (1536, 864, 120),
        (1536, 864, 150), 
        (1280, 720, 120),
        (640, 480, 200),
        (640, 480, 240),
    ]
    
    results = []
    for w, h, fps in modes:
        actual = test_fps_rpicam(w, h, fps)
        if actual:
            results.append((w, h, fps, actual))

    print("\nSummary:")
    for w, h, req, act in results:
        print(f"{w}x{h}: Requested {req}, Got {act:.2f}")
