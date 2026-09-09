# 🔌 SafeRide AI — REST API Reference

The SafeRide AI backend exposes a REST API built with **FastAPI** (`api.py`) for communication between native Android mobile clients, IoT on-board telematics units (OBD), and the dispatch platform.

---

## Base URL & Authentication

```
Base URL: http://<server-host>:8000/api/v1
```

### Authentication Header
Endpoints requiring security utilize HTTP Bearer Token authentication. If `SAFERIDE_API_TOKEN` is set in `.env`, include the token in all requests:

```http
Authorization: Bearer <YOUR_SAFERIDE_API_TOKEN>
```

---

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/health` | Server & database health check | No |
| `POST` | `/incidents` | Create a new crash or SOS incident | Yes |
| `GET` | `/incidents` | List all reported incidents | Yes |
| `GET` | `/incidents/{incident_id}` | Fetch detailed incident info | Yes |
| `PUT` | `/incidents/{incident_id}/location` | Stream live GPS coordinate updates | Yes |
| `POST` | `/incidents/{incident_id}/audio` | Upload voice memo / ambient audio | Yes |

---

## Detailed Endpoint Specifications

### 1. Health Check
`GET /api/v1/health`

#### Response: `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "timestamp": "2026-09-09T13:20:00Z"
}
```

---

### 2. Create Incident
`POST /api/v1/incidents`

Used by mobile clients or IoT sensors upon crash detection or manual SOS activation.

#### Request Body:
```json
{
  "vehicle_type": "Motorcycle",
  "latitude": 17.4435,
  "longitude": 78.3772,
  "confidence": 98.0,
  "rider_status": "NEED HELP",
  "language": "English",
  "message": "High-impact collision detected (4.2G, 65° tilt).",
  "speed_before": 87.0,
  "speed_after": 0.0,
  "impact_force_g": 4.2,
  "tilt_angle_deg": 65.0
}
```

#### Response: `201 Created`
```json
{
  "incident_id": "INC-20260909-319501",
  "status": "REPORTED",
  "confidence": 98.0,
  "address": "12 MG Road, Bengaluru",
  "created_at": "2026-09-09T13:20:05Z",
  "dispatch_initiated": true
}
```

#### Example cURL:
```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my_secret_token" \
  -d '{
    "vehicle_type": "Motorcycle",
    "latitude": 17.4435,
    "longitude": 78.3772,
    "confidence": 98.0,
    "rider_status": "NEED HELP"
  }'
```

---

### 3. Update Incident Location
`PUT /api/v1/incidents/{incident_id}/location`

Stream live GPS coordinates while an incident is active to track rider drift or ambulance transit.

#### Request Body:
```json
{
  "latitude": 17.4438,
  "longitude": 78.3775,
  "speed": 0.0,
  "accuracy_m": 3.5
}
```

#### Response: `200 OK`
```json
{
  "incident_id": "INC-20260909-319501",
  "latitude": 17.4438,
  "longitude": 78.3775,
  "updated_at": "2026-09-09T13:20:10Z"
}
```

---

### 4. Upload Incident Audio
`POST /api/v1/incidents/{incident_id}/audio`

Uploads an ambient audio clip or rider voice response captured post-incident for speech-to-text processing.

#### Request:
- Content-Type: `multipart/form-data`
- Form field: `audio_file` (WAV, MP3, or AAC file)

#### Response: `200 OK`
```json
{
  "incident_id": "INC-20260909-319501",
  "audio_id": "AUD-98214",
  "transcript": "Help, I crashed on the corner of MG Road, leg is trapped.",
  "language_detected": "English",
  "translated_te": "సహాయం, నేను ఎంజీ రోడ్ మూలలో ప్రమాదానికి గురయ్యాను, కాలు ఇరుక్కుపోయింది."
}
```
