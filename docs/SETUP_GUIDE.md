# 🛠️ SafeRide AI — Developer Setup & Installation Guide

This guide walks you through setting up and running all SafeRide AI services locally on Windows, macOS, or Linux.

---

## 1. Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 installed
- **Git**: For cloning the repository
- **Twilio Account**: (Optional for simulation, required for live voice calls & SMS)
- **Geoapify API Key**: (Optional, system automatically falls back to OSM Nominatim if omitted)
- **Android Studio**: (Only required if building the native Kotlin Android app)

---

## 2. Clone & Environment Setup

```bash
# Clone the repository
git clone https://github.com/rangithkumarpathyam-collab/ride-safe.git
cd ride-safe

# Create and activate Python virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

## 3. Environment Variables Configuration (`.env`)

Create or edit your `.env` file in the root of the project:

```ini
# Twilio Programmable Voice & SMS Gateway
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
EMERGENCY_DISPATCH_PHONE=+917416960828

# Reverse Geocoding API (Geoapify)
GEOAPIFY_API_KEY=your_geoapify_api_key_here

# Security Token for Mobile Client REST API
SAFERIDE_API_TOKEN=your_secure_random_token_here
```

> **Note**: If you don't have Twilio credentials yet, the application gracefully operates in **Simulation Mode** — logging all outgoing calls, TwiML scripts, and SMS alerts directly to the console and database without raising errors.

---

## 4. Running the Applications

SafeRide AI consists of three interconnected services:

### A. Mobile Companion & Glass White UI (Port 8502)
Run the rider mobile interface:
```bash
python -m streamlit run mobile_app.py --server.port 8502
```
Open **`http://localhost:8502`** in your browser.

### B. Operations Dispatch Command Center (Port 8501)
Run the dispatcher terminal:
```bash
python -m streamlit run app.py --server.port 8501
```
Open **`http://localhost:8501`** in your browser.

### C. FastAPI Backend REST Server (Port 8000)
Run the telemetry ingestion server for Android clients:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API documentation available at **`http://localhost:8000/docs`**.

---

## 5. Building the Native Android App (`android-app/`)

1. Open Android Studio.
2. Select **Open an Existing Project** and browse to `c:\Users\ranjith kumar\Desktop\ride sheild\android-app`.
3. In `local.properties`, configure your local server IP (e.g. `API_BASE_URL="http://192.168.1.50:8000/api/v1/"`).
4. Sync Gradle dependencies:
   ```bash
   ./gradlew assembleDebug
   ```
5. Run on an Android device or emulator (Android 9.0+ / API 28+ recommended).

---

## 6. Verification & Health Check

1. Verify SQLite database:
   ```bash
   python -c "import database as db; db.init_db(); print('DB OK')"
   ```
2. Verify AI crash detection module:
   ```bash
   python -c "import accident_detection as ad; print(ad.detect_accident(80, 0, 4.5, 60, 'Motorcycle'))"
   ```
3. Test Twilio SMS dispatch in terminal:
   ```bash
   python -c "import notifications as n; print(n.send_emergency_sms({'incident_id':'TEST-01','confidence':95,'latitude':17.44,'longitude':78.37}))"
   ```
