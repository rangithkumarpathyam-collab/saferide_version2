# 📱 Mobile Experience & Glass White UI Design System

## Overview

The SafeRide AI mobile experience is engineered around a modern **Glass White** visual hierarchy inspired by cutting-edge Figma glassmorphic design principles. The design emphasizes ultra-clean light backgrounds, soft frosted blurs, bold typography, tactile micro-interactions, and a persistent floating bottom navigation dock.

---

## Design System & Tokens

### Color Palette

| Token | Hex / Value | Role |
| :--- | :--- | :--- |
| `--bg-dark` | `#f8fafc` | Canvas background with subtle radial blue glow |
| `--glass-card` | `rgba(255, 255, 255, 0.94)` | Frosted white glass cards with soft drop shadows |
| `--glass-border` | `rgba(226, 232, 240, 0.90)` | Subtle light borders separating panels |
| `--accent-cyan` | `#0284c7` | Brand primary color & active GPS telemetry highlights |
| `--accent-emerald`| `#059669` | Nominal telemetry state & confirmed safety badges |
| `--accent-red` | `#dc2626` | Emergency SOS triggers & critical crash badges |
| `--accent-amber` | `#d97706` | Elevated impact warnings & AI latency meters |
| `--text-main` | `#0f172a` | Primary headings, values, and high-contrast labels |
| `--text-muted` | `#64748b` | Supporting captions, subtitles, and telemetry units |

---

## Screen Architecture

### 1. 🏠 Home Screen (`Home`)
- **Hero Confidence Horseshoe Gauge**:
  - Custom SVG horseshoe track with an emerald gradient progress stroke representing real-time telemetry confidence (nominal: 98%).
  - Text stack (`NOMINAL`, `98%`, `CONFIDENCE`) centered inside the arc with generous vertical margins to prevent visual overlap.
  - "ALL TELEMETRY NOMINAL" status badge with animated pulse.
- **2x2 Telemetry HUD Tiles**:
  - **Speed**: Real-time velocity (`50 km/h`).
  - **Peak G-Force**: Impact vector magnitude (`1.5 G`) with amber progress track.
  - **Lean Angle**: Horizon tilt indicator (`26°`) with an interactive slider track.
  - **Impact State**: Gravitational delta (`0.0 G`, "Threshold safe").
- **High-Priority Dispatch Card**: Overview of the automated Twilio emergency calling service.
- **1-Click SOS Trigger**: Button to manually engage the 10-second emergency dispatch timer.
- **Women Safety Emergency Section**: Direct voice & SMS activation with quick dial button.

### 2. 🚨 Alerts & Incident Detail Screen (`Alerts`)
- **Active Incident Header**: Incident ID badge with critical status indicator.
- **Rider Profile Card**: Displays rider name (Anand Verma), vehicle details, emergency status, and a 1-click phone shortcut.
- **Reverse Geocoded Address**: Full street-level physical location (`12 MG Road, Bengaluru`).
- **Telemetry Breakdown**: Pre-impact speed, post-impact speed, and resultant G-forces.
- **AI Confidence Meter**: Visual gradient bar showing accident probability.
- **Quick Action Grid**: One-tap triggers for `108 Ambulance`, `SMS`, `Twilio Call`, and `Mark Resolved`.
- **Action Timeline**: Real-time chronological audit trail of responder actions.

### 3. 🗺️ Live GIS Radar Tracker (`Map`)
- **Leaflet / OSM Interactive Map**: Displays the crash coordinates with radar perimeter rings (350m inner zone, 750m mutual-aid zone).
- **Search Bar**: Quick lookup for nearby hospitals, police stations, and landmarks.
- **Incident Summary Card**: Compact overlay with instant dispatch CTA.

### 4. ⚡ Crash Simulator (`Sim`)
- **Preset Selector**: Test scenarios including *Severe T-Bone Collision*, *Low-Speed Laydown*, *Pothole Jolt*, *Emergency Hard Braking*, and *Rear-End Impact*.
- **Telemetry Sliders**: Real-time manipulation of Speed Before (0-160 km/h), Speed After (0-160 km/h), Impact Force (0.5-12.0 G), and Tilt Angle (0-90°).
- **Live AI Confidence Meter**: Dynamically computes crash probability and auto-engages emergency SOS if confidence exceeds 70%.

### 5. 🌸 Women Safety Shield (`Women`)
- **Instant Emergency Dispatch**: High-priority automated Twilio voice call and GPS SMS broadcasting to designated responders and police networks.
- **Direct Emergency Helplines**: High-contrast, tactile cards for `1091 Women Helpline`, `112 Police/All SOS`, `108 Ambulance`, and `Dispatcher`.
- **Live GPS Fix**: Coordinate readout with Google Maps turn-by-turn routing link.

### 6. ⚙️ Settings & Calibration Console (`Settings`)
- **Rider Profile**: Alex Turner (`Yamaha MT-07`, `KA-01-EQ-4291`, `O+ Positive`, 1,240 km monitored, 98% Safety Index).
- **Twilio Emergency Gateway**: Editable primary dispatch number, secondary guardian contact, SOS countdown duration (5s, 10s, 15s, 30s), automated voice call toggles, SMS broadcast toggles, and live "Test Twilio Call" verification button.
- **Sensor Calibration & AI Tuning**: Sliders for confidence threshold (50-95%), peak impact trigger (2.0-7.5G), horizon tilt angle (45-85°), deceleration delta, plus pothole & speed-breaker rejection filters.
- **Display & Audio Preferences**: Theme selection (Glass White vs Cyber Dark), siren audio toggles, haptic vibration pulses, metric/imperial units.
- **Hardware Diagnostics**: Real-time connectivity badges for RTK Satellite GPS (14 satellites, ±0.4m), 6-Axis IMU (100Hz calibrated), Twilio TLS Webhook, and SQLite encrypted cache.

---

## Persistent Floating Bottom Navigation Dock

The navigation dock remains fixed across all views with the following characteristics:
- **Frosted Glass Styling**: `background: rgba(255, 255, 255, 0.95)`, `backdrop-filter: blur(24px)`, pill border radius (`999px`), subtle drop shadow (`0 12px 36px rgba(0,0,0,0.08)`).
- **Dock Icons**:
  1. ⌂ `Home`: Main telemetry dashboard.
  2. ! `Alerts`: Active incident details & timeline.
  3. 🚨 `SOS` (Center): Elevated ruby circular badge with glow animation for instant emergency trigger.
  4. ⌖ `Map`: Live GIS radar tracker.
  5. ⚙️ `Settings`: Profile, hardware diagnostics, and sensor tuning.
- **Active Dot Indicator**: An emerald dot indicates the currently active section.
- **Page Bottom Clearance**: Every page has `6.5rem` bottom padding to guarantee interactive elements never hide behind the dock.
