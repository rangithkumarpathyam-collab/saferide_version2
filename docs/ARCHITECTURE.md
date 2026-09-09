# 🏛️ System Architecture — SafeRide AI

## Overview

SafeRide AI is a distributed, multimodal accident detection and emergency response system. It connects IoT/mobile vehicle sensors, artificial intelligence algorithms, telecommunications gateways, cloud GIS services, and emergency dispatch centers into a cohesive, fault-tolerant life-saving pipeline.

```
+-------------------------------------------------------------------------------+
|                             RIDER & VEHICLE SENSORS                           |
|       (6-Axis IMU, GPS Telematics, CameraX, Bluetooth OBD, Speedometer)       |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                       EDGE / MOBILE SENSOR FUSION ENGINE                      |
|           • Fast Accident Classifier (Speed Drop, G-Force, Tilt Angle)        |
|           • Transient Pothole & Road-Bump False Positive Rejection            |
|           • 10-Second Abortable Emergency SOS Countdown Shield                |
+-------------------------------------------------------------------------------+
                                      |
                         HTTP / REST API (FastAPI)
                                      v
+-------------------------------------------------------------------------------+
|                         SAFERIDE BACKEND & DISPATCH CORE                      |
|                                                                               |
|  [FastAPI Endpoints]        [SQLite Telemetry Cache]    [Geoapify & OSM GIS]  |
|  • /api/v1/incidents        • saferide.db (WAL mode)    • Reverse Geocoding   |
|  • /api/v1/location         • Incidents, Telemetry,     • Street Address Fix  |
|  • /api/v1/audio            • Audit Trail, Audio Logs   • Incident Perimeter  |
+-------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+------------------------------------+   +--------------------------------------+
|       TELECOMS CLOUD GATEWAY       |   |     OPERATOR COMMAND & CONTROL       |
|             (Twilio)               |   |            (Streamlit)               |
|  • Automated TwiML Voice Calling   |   |  • Live Interactive Leaflet Map      |
|  • High-Priority Location SMS      |   |  • Real-Time Incident Priority Queue |
|  • WhatsApp Live Route Broadcast   |   |  • Audio Playback & Voice Transcripts|
|  • Regional Emergency Relays (112) |   |  • Neural Regional Translation       |
+------------------------------------+   +--------------------------------------+
```

---

## Core Components

### 1. Accident Detection & Telemetry Fusion (`accident_detection.py`)
- **Tri-Vector Sensor Fusion**:
  - Velocity drop delta ($\Delta V = V_{\text{before}} - V_{\text{after}}$).
  - Peak resultant impact force vector ($\vec{G} = \sqrt{a_x^2 + a_y^2 + a_z^2}$).
  - Lateral/horizontal tilt lay-down angle ($\theta = \arccos(a_z / |\vec{a}|)$).
- **Vehicle Type Heuristics**: Dynamic thresholds adjusted for Motorcycles, Cars, Auto-Rickshaws, and Buses.
- **Pothole/Speed-Breaker Rejection**: Uses vertical spike duration filters to differentiate momentary road bumps from actual collisions.

### 2. Telecommunications Gateway (`notifications.py`)
- **Twilio Programmable Voice**: Generates on-the-fly TwiML speech synthesis with Alice (`en-IN`, `hi-IN`, `te-IN`), announcing exact rider identity, vehicle plate, coordinates, and verified address to police and dispatchers.
- **Priority Emergency SMS**: Broadcasts Google Maps GPS links (`https://maps.google.com/?q=lat,lon`) to designated emergency contacts.
- **WhatsApp Live Route Broadcast**: Pre-formats turn-by-turn routing payload for emergency responders.

### 3. GIS Mapping & Geocoding (`geocoding.py`)
- **Dual Reverse Geocoding Engine**: Geoapify API with automatic fallback to OpenStreetMap (OSM) Nominatim. Converts raw latitude/longitude into postal street addresses, corridor names, and landmark descriptions.
- **Haversine Distance Tracking**: Computes proximity between dispatched ambulances and incident coordinates in real time.

### 4. Incident Database & Audit Store (`database.py`)
- **Schema**:
  - `incidents`: Incident ID, vehicle type, confidence score, status (`REPORTED`, `DISPATCHED`, `RESOLVED`), timestamp, reverse-geocoded address, rider status.
  - `telemetry`: High-frequency speed, G-force, tilt angle, and sensor logs.
  - `chat_messages`: Multilingual responder-rider communication threads.
  - `audio_logs`: Stored audio waveforms and speech-to-text transcriptions.

### 5. Mobile Companion & Glass White UI (`mobile_app.py`)
- High-fidelity mobile interface preview following modern Figma Glass White design tokens.
- Floating frosted-glass capsule navigation dock with active glow indicators.
- 10-second countdown emergency abort banner.
- Dedicated Women Safety Shield with rapid helplines (`1091`, `112`, `108`).
- Full system configuration console for sensor threshold tuning and Twilio gateway controls.

### 6. Central Dispatcher Command Center (`app.py`)
- Operator web dashboard for fleet monitoring and emergency management.
- Real-time incident triage table, Leaflet GIS map with radar perimeters, responder dispatch buttons, and Telugu-English bidirectional neural translation.

### 7. RESTful API Server (`api.py`)
- FastAPI-powered backend with bearer token authentication for native Android and IoT edge device integrations.
