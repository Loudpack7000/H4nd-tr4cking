# Hand Tracking & Vision Dashboard

This project provides a real-time vision dashboard and an AI Hand DJ interface designed for the Raspberry Pi 5 with an IMX708 camera.

## How to use

### 1. Connecting the Hardware
- If you are using the Raspberry Pi, ensure the camera is connected.
- If you are using a laptop, the server will automatically fallback to use your built-in webcam.

### 2. Installation
Install the necessary Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Server
Start the dashboard from the `camera_dashboard` directory:
```bash
python3 server.py
```

### 4. Accessing the UI
Open your browser and navigate to:
- **Local (on the same device):** `http://localhost:8000`
- **Network (from your laptop while Pi is plugged in):** `http://<pi_ip_address>:8000`

## Features
- **Vision Core:** High-speed 60fps MJPEG stream.
- **Hand Vision DJ:** Uses MediaPipe for hand tracking to control a Web Audio synthesizer.
  - **Left Hand:** Open/Close fingers to control synth voices.
  - **Right Hand:** Pinch to control global frequency.
