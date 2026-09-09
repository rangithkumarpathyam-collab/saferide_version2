# 🛡️ SafeRide AI — Multimodal Autonomous Emergency Response Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Twilio Voice & SMS](https://img.shields.io/badge/Twilio-Voice%20%26%20SMS-F22F46.svg)](https://www.twilio.com/)
[![GIS Mapping](https://img.shields.io/badge/GIS-Leaflet%20%26%20OSM-brightgreen.svg)](https://leafletjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SafeRide AI** is a distributed, multimodal emergency detection and rapid response system. Designed primarily for two-wheeler and commercial motorists, it pairs real-time vehicle telematics sensor fusion with cloud telecommunications gateways to detect crashes within milliseconds, initiate automated emergency voice dispatch, and broadcast turn-by-turn routing to first responders and police networks.

---

## 🌟 Core System Highlights

- **🧠 Tri-Vector Sensor Fusion Engine**: Synthesizes velocity deceleration ($\Delta V$), peak resultant impact forces ($G_{\text{res}}$), and horizon lean/tilt angles ($\theta$) to assess collision probability.
- **🛡️ 10-Second Abortable SOS Shield**: Provides an automated visual and high-decibel audible countdown, enabling conscious riders to cancel false alarms before emergency dispatch fires.
- **📞 Autonomous Twilio Cloud Gateway**: Places speech-synthesized TwiML phone calls to emergency dispatchers (`108` / regional dispatch) with live incident coordinates and verified street addresses.
- **🌸 Dedicated Women Safety Shield**: One-tap rapid voice/SMS distress trigger with direct high-contrast speed-dial access to `1091 (Women Helpline)`, `112 (Police/All SOS)`, and `108 (Ambulance)`.
- **🗺️ Live GIS Mapping & Geocoding**: Dual-engine reverse geocoding (Geoapify + OSM Nominatim) converts raw GPS telemetry into street corridors, rendered on Leaflet interactive radar maps.
- **🎨 Modern Glass White Mobile Design System**: High-fidelity mobile companion inspired by Figma Glass White aesthetics, featuring a persistent floating frosted-glass navigation dock.
- **💬 Multilingual Neural Translation Hub**: Bidirectional Telugu ↔ English neural translation enabling regional riders to communicate seamlessly with dispatch centers.

---

## 📸 System Preview & Screen Gallery

| View | Screenshot / Feature | Description |
| :--- | :---: | :--- |
| **Home Dashboard** | `preview_home_top` | Circular SVG horseshoe confidence gauge (98% nominal) with zero-stroke collision, telemetry status, and ARMED indicator. |
| **Telemetry HUD** | `preview_home_scrolled` | 2x2 live telemetry tiles (Speed, Peak G-Force, Lean Angle, Impact State) and high-priority dispatch warnings. |
| **Settings & Calibration** | `preview_settings_top` | Rider profile (Alex Turner, Yamaha MT-07, KA-01-EQ-4291, Blood Group O+), Twilio gateway phone configurations, and voice alert options. |
| **Sensor AI Tuning** | `preview_settings_bottom` | Real-time threshold sliders for AI confidence, peak G-force, tilt angles, false-alarm bump filters, and hardware diagnostics. |
| **Alerts & Timeline** | `preview_alerts` | Anand Verma incident report, high-contrast telemetry readout, speed before/after comparison, and responder action timeline. |
| **Women Safety Shield** | `preview_women_safety` | Instant emergency dispatch CTA, high-contrast helpline tiles (`1091`, `112`, `108`, `Dispatcher`), and live GPS fix. |
| **Live GIS Radar Map** | `preview_map` | Leaflet dark-matter radar map with incident perimeter rings (350m inner, 750m mutual-aid zone) and search bar. |

---

## 🏗️ Architectural Flow

```
+-------------------+        +----------------------------+        +--------------------------+
|  Vehicle Sensors  | -----> |  AI Sensor Fusion Engine   | -----> | 10s Abortable SOS Banner |
| (IMU, GPS, Speed) |        | (accident_detection.py)    |        | (mobile_app.py / app.py) |
+-------------------+        +----------------------------+        +--------------------------+
                                                                                 |
                                                                       Timeout / Triggered
                                                                                 v
+-------------------+        +----------------------------+        +--------------------------+
| Dispatch Terminal | <----- | SQLite Incident Audit DB   | <----- | Twilio Gateway & GIS     |
| (Port 8501)       |        | (saferide.db)              |        | (Voice, SMS, Geoapify)   |
+-------------------+        +----------------------------+        +--------------------------+
```

---

## 🗂️ Project Repository Structure

```
ride-shield/
├── accident_detection.py      # AI sensor fusion & crash classification algorithms
├── api.py                     # FastAPI REST API server for Android / IoT clients
├── app.py                     # Dispatcher Command & Control Center (Port 8501)
├── database.py                # SQLite persistence layer (incidents, telemetry, logs)
├── geocoding.py               # Geoapify & OSM Nominatim reverse geocoding engine
├── mobile_app.py              # Glass White Mobile Companion & Preview (Port 8502)
├── notifications.py           # Twilio Voice (TwiML), SMS, and WhatsApp dispatch
├── translation.py             # Multilingual regional neural translation engine
├── requirements.txt           # Python dependency requirements
├── setup_mobile_connection.bat# Quick launcher for local mobile pairing
├── saferide.db                # SQLite database file
├── .env                       # Local environment variables & API tokens
├── docs/                      # Comprehensive technical documentation
│   ├── ARCHITECTURE.md        # Deep-dive system architecture & data pipeline
│   ├── MOBILE_APP.md          # Mobile UI design system & Glass White tokens
│   ├── API_REFERENCE.md       # FastAPI endpoint specifications & cURL examples
│   ├── SENSOR_FUSION_AI.md    # Physics formulas, G-force vectors & AI heuristics
│   └── SETUP_GUIDE.md         # Complete step-by-step developer installation guide
└── android-app/               # Native Android Kotlin application codebase
    ├── app/                   # Android app source (Kotlin, CameraX, Sensors)
    ├── build.gradle.kts       # Gradle build configuration
    └── settings.gradle.kts    # Android project settings
```

---

## ⚡ Quick Start Guide

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/rangithkumarpathyam-collab/ride-safe.git
cd ride-safe

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials (`.env`)
Create a `.env` file in the project root:
```ini
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
EMERGENCY_DISPATCH_PHONE=+917416960828
GEOAPIFY_API_KEY=your_geoapify_key
SAFERIDE_API_TOKEN=your_secret_token
```
*(If Twilio keys are omitted, the platform runs in full Simulation Mode without crashing.)*

### 3. Launch Services

#### Launch Mobile Companion & Glass White UI:
```bash
python -m streamlit run mobile_app.py --server.port 8502
```
Access at **`http://localhost:8502`**.

#### Launch Central Dispatch Command Center:
```bash
python -m streamlit run app.py --server.port 8501
```
Access at **`http://localhost:8501`**.

#### Launch Backend REST API:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation at **`http://localhost:8000/docs`**.

---

## 📚 Technical Documentation Directory

For in-depth guides and references, explore the **`docs/`** directory:

- 🏛️ **[System Architecture](docs/ARCHITECTURE.md)**: Data pipelines, component interactions, and failure modes.
- 📱 **[Mobile Experience & Glass White UI](docs/MOBILE_APP.md)**: Design tokens, floating dock, and component layouts.
- 🔌 **[REST API Reference](docs/API_REFERENCE.md)**: Complete endpoint schemas, authentication, and payloads.
- 🧠 **[Sensor Fusion & AI Engine](docs/SENSOR_FUSION_AI.md)**: Mathematical formulas, G-force vectors, and shock filters.
- 🛠️ **[Developer Installation Guide](docs/SETUP_GUIDE.md)**: Local setup, testing routines, and Android builds.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.
