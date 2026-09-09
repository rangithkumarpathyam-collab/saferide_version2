# 🧠 Sensor Fusion & AI Accident Detection Engine

## Overview

The SafeRide AI accident detection engine (`accident_detection.py`) combines raw high-frequency telematics data from vehicle sensors and mobile device IMUs (Inertial Measurement Units) to accurately determine crash probability within milliseconds.

---

## 1. Mathematical Formulas & Telematics Vectors

### A. Velocity Deceleration Delta ($\Delta V$)
Severe accidents typically exhibit extreme negative acceleration where velocity plummets within fractions of a second:

$$\Delta V = \max(0, V_{\text{before}} - V_{\text{after}})$$

The deceleration score $S_{\text{speed}}$ is calculated as:

$$S_{\text{speed}} = \min\left(100, \left(\frac{\Delta V}{\Delta V_{\text{crit}}}\right) \times 100\right)$$

Where $\Delta V_{\text{crit}} = 50\text{ km/h}$. For motorcycle collisions, an instant speed drop exceeding $35\text{ km/h}$ enters the critical probability band.

---

### B. Impact Vector Magnitude ($G_{\text{res}}$)
The 3-axis accelerometer measures acceleration along orthogonal axes $(a_x, a_y, a_z)$ in units of gravity ($1G \approx 9.81\text{ m/s}^2$):

$$G_{\text{res}} = \sqrt{a_x^2 + a_y^2 + a_z^2}$$

The impact severity score $S_{\text{impact}}$ is evaluated against nominal and critical impact ceilings:

$$S_{\text{impact}} = \min\left(100, \left(\frac{G_{\text{res}} - G_{\text{baseline}}}{G_{\text{crit}} - G_{\text{baseline}}}\right) \times 100\right)$$

- Normal riding vibrations: $0.8G - 1.8G$
- Road potholes & speed bumps: $1.8G - 2.8G$
- Vehicular collision: $3.5G - 12.0G+$

---

### C. Horizon Tilt Lay-Down Angle ($\theta$)
A primary indicator of two-wheeler crashes is severe tilt or lateral recumbency:

$$\theta = \arccos\left(\frac{a_z}{G_{\text{res}}}\right) \times \left(\frac{180}{\pi}\right)$$

$$S_{\text{tilt}} = \begin{cases} 
0, & \theta < 35^\circ \\
\left(\frac{\theta - 35^\circ}{90^\circ - 35^\circ}\right) \times 100, & 35^\circ \le \theta \le 90^\circ 
\end{cases}$$

---

## 2. Dynamic Vehicle Weighting & Heuristics

Different vehicle categories have distinct dynamics during an incident. The composite confidence score $C$ is a weighted fusion:

$$C = w_v \cdot S_{\text{speed}} + w_g \cdot S_{\text{impact}} + w_t \cdot S_{\text{tilt}}$$

| Vehicle Type | $w_v$ (Speed) | $w_g$ (Impact) | $w_t$ (Tilt) | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Motorcycle** | 0.35 | 0.40 | 0.25 | Tilt is crucial for two-wheelers |
| **Car** | 0.45 | 0.50 | 0.05 | Cars rarely flip sideways in low-speed impacts |
| **Auto-Rickshaw** | 0.35 | 0.45 | 0.20 | 3-wheelers prone to rollover |
| **Bus / Heavy** | 0.50 | 0.50 | 0.00 | Focus on massive deceleration and structural shock |

---

## 3. False-Positive Rejection (Pothole & Speed-Breaker Filter)

A major hurdle in crash detection systems is false triggers caused by potholes, rough pavement, or speed breakers.

SafeRide AI utilizes a **Temporal Shock Filter**:
- **Transient Shock Signature**: Potholes cause an isolated vertical spike ($a_z > 2.5G$) with very short duration ($t < 80\text{ ms}$) without a corresponding velocity collapse ($\Delta V \approx 0$).
- **Collision Signature**: True accidents produce sustained multi-axis deceleration and structural impulse ($t > 150\text{ ms}$) accompanied by $\Delta V > 25\text{ km/h}$ and post-event vehicle immobilization ($V_{\text{after}} \approx 0$).

If a high G-force spike occurs while speed remains continuous ($\Delta V < 10\text{ km/h}$), the confidence score is automatically suppressed below the emergency SOS threshold ($C < 40\%$).

---

## 4. Severity Classification Tiers

| Confidence Score | Status Tier | System Action |
| :---: | :---: | :--- |
| **$\ge 70\%$** | 🔴 **CRITICAL** | Automatically arms 10s countdown banner; triggers Twilio voice call & SMS to dispatch upon timeout |
| **$45\% - 69\%$** | 🟡 **ELEVATED / WARNING** | Logs telemetry event to SQLite; notifies rider of high shock; no automatic dispatch |
| **$< 45\%$** | 🟢 **NOMINAL** | Normal riding telematics; background continuous logging |
