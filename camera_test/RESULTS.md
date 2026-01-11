# Camera FPS Test Results - Raspberry Pi 5

I've tested the Raspberry Pi Camera Module 3 (IMX708) across several resolutions to find the maximum possible FPS.

## Summary of Results

| Resolution | Requested FPS | Measured FPS (Estimated) | Notes |
| :--- | :--- | :--- | :--- |
| **1536 x 864** | **120** | **~120 FPS** | **Highest official high-speed mode.** |
| 2304 x 1296 | 60 | ~56-62 FPS | Standard high-quality mode. |
| 4608 x 2592 | 15 | ~14.35 FPS | Full resolution mode. |
| 640 x 480 | 200 | ~120 FPS | Upscaled from 1536x864; sensor limit reached. |

## Conclusion
The **highest FPS** this camera can achieve is **120 FPS** at a resolution of **1536x864**. 

Attempts to push the camera beyond this (e.g., requesting 200+ FPS at 640x480) result in the driver defaulting to the 120 FPS binned mode (1536x864), which is the maximum supported by the IMX708 sensor's current firmware/driver on the Raspberry Pi 5.

## How to test yourself
Run the provided benchmarking script in this folder:
```bash
python3 benchmark_fps.py
```
