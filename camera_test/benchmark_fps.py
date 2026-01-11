import subprocess
import time
import os

def run_benchmark(width, height, requested_fps, frames=600):
    print(f"--- Benchmarking: {width}x{height} @ {requested_fps} FPS ---")
    
    # We use rpicam-vid with yuv420 codec to /dev/null as it's a good balance of speed and realism
    # and we use --libav-format rawvideo to avoid container overhead
    cmd = [
        "rpicam-vid",
        "--frames", str(frames),
        "--nopreview",
        "--width", str(width),
        "--height", str(height),
        "--framerate", str(requested_fps),
        "--codec", "yuv420",
        "--denoise", "cdn_off",
        "--awb", "indoor",
        "--shutter", "1000", # 1ms exposure to ensure it's not the bottleneck
        "-o", "/dev/null",
        "--libav-format", "rawvideo"
    ]
    
    start_time = time.time()
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        if process.returncode != 0:
            print(f"Error: {process.stderr}")
            return None
        
        # Estimate startup time (usually ~0.8s to 1.2s on Pi 5)
        # To be more accurate, we should really measure from the first frame, 
        # but for a quick test, this is okay.
        total_duration = end_time - start_time
        
        # We'll assume a 1 second overhead for setup/init
        effective_duration = max(0.1, total_duration - 1.0) 
        estimated_fps = frames / effective_duration
        
        # Raw FPS (including startup)
        raw_fps = frames / total_duration
        
        print(f"  Total Time:     {total_duration:.2f}s")
        print(f"  Raw FPS:        {raw_fps:.2f} (includes startup overhead)")
        print(f"  Estimated FPS:  {estimated_fps:.2f} (excludes ~1s startup)")
        print("-" * 40)
        return estimated_fps
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    print("Raspberry Pi 5 Camera FPS Benchmark")
    print("=" * 40)
    
    test_modes = [
        (1536, 864, 120),  # High speed mode
        (2304, 1296, 60),  # Standard mode
        (4608, 2592, 15),  # High res mode
        (640, 480, 200),   # Custom push
    ]
    
    for w, h, fps in test_modes:
        run_benchmark(w, h, fps)
    
    print("\nNote: The IMX708 sensor is officially capped at 120 FPS in binned mode (1536x864).")
