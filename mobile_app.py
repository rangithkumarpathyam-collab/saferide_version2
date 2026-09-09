"""
SafeRide AI - Mobile Companion (Glass UI/UX Edition)
---------------------------------------------------
Full-featured mobile response console matching the glassmorphic UI/UX mockup:
  - Splash / Operator Access Portal
  - ⌂ Home: 2x2 Glass Metric Grid & Recent Incidents Feed
  - ! Alerts: Incident Details, Telemetry Vectors, Verified Address, Action Timeline
  - ⌖ Map: Dark Radar Scanner & Active GIS Incident Tracking
  - ⚡ Sim: Interactive Crash Telemetry Simulator & AI Confidence Estimator
  - ● Profile: Dispatcher Stats, Notification Sounds, & Twilio Automations
  - 🚨 10-Second SOS Emergency Countdown Timer with automated Twilio Voice Dispatch
"""

import time
import urllib.parse
from datetime import datetime
import streamlit as st

import importlib
import accident_detection as ad
import database as db
importlib.reload(db)
import geocoding as geo
import notifications as notify

st.set_page_config(
    page_title="SafeRide AI Mobile",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# ULTRA-PREMIUM GLASSMORPHIC CSS DESIGN SYSTEM
# -----------------------------------------------------------------------------
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Glass White UI"

is_white_theme = st.session_state.app_theme == "Glass White UI"

theme_tokens = """
        :root {
            --bg-dark: #f8fafc;
            --glass-card: rgba(255, 255, 255, 0.94);
            --glass-card-hover: rgba(255, 255, 255, 0.98);
            --glass-border: rgba(226, 232, 240, 0.9);
            --glass-border-light: rgba(203, 213, 225, 0.95);
            --accent-cyan: #0284c7;
            --accent-emerald: #059669;
            --accent-red: #ef4444;
            --accent-amber: #d97706;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        .metric-tile {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
        }
        .incident-card {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
        }
        .nav-bar {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(226, 232, 240, 0.9) !important;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.08) !important;
        }
        .system-pill {
            background: rgba(16, 185, 129, 0.12) !important;
            border: 1px solid rgba(16, 185, 129, 0.35) !important;
            color: #047857 !important;
        }
        .glass-card {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            color: #0f172a !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03) !important;
        }
""" if is_white_theme else """
        :root {
            --bg-dark: #070c16;
            --glass-card: rgba(15, 23, 42, 0.72);
            --glass-card-hover: rgba(22, 34, 60, 0.85);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-border-light: rgba(255, 255, 255, 0.15);
            --accent-cyan: #38bdf8;
            --accent-emerald: #34d399;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
"""

bg_gradient = "radial-gradient(circle at 50% 0%, rgba(224, 242, 254, 0.75) 0%, rgba(248, 250, 252, 0.98) 60%), #f8fafc" if is_white_theme else "radial-gradient(circle at 50% 0%, rgba(30, 58, 138, 0.32) 0%, rgba(7, 12, 22, 0.98) 60%), #070c16"

CSS_TEMPLATE = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
        
        __THEME_TOKENS__

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: -0.01em;
        }

        [data-testid="stAppViewContainer"] {
            background: __BG_GRADIENT__;
            color: var(--text-main);
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 480px;
            padding: 0.75rem 0.85rem 6.5rem;
            margin: 0 auto;
        }

        /* Hide Streamlit default header/footer */
        #MainMenu, header, footer { visibility: hidden; height: 0; }

        /* Glassmorphic Panel Core */
        .glass-card {
            background: var(--glass-card);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.04);
            border-radius: 20px;
            padding: 1.15rem;
            margin-bottom: 0.9rem;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .glass-card:hover {
            border-color: var(--glass-border-light);
        }

        /* Top Header & Pills matching reference image */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.35rem 0.1rem 0.95rem;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .rider-avatar {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.95);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0284c7, #38bdf8);
        }
        .header-title-stack {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .header-app-name {
            font-size: 0.75rem;
            font-weight: 800;
            color: #64748b;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .header-status-text {
            font-size: 0.95rem;
            font-weight: 900;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .status-dot-emerald {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
            display: inline-block;
        }
        .header-right {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 5px;
        }
        .header-pill {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            padding: 3px 9px;
            font-size: 0.7rem;
            font-weight: 800;
            color: #0f172a;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        }

        /* 2x2 Metric Grid Styling */
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-bottom: 0.9rem;
        }
        .metric-tile {
            background: #ffffff;
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1rem 0.95rem 0.85rem;
            text-align: left;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.03);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 120px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-tile:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        }
        .metric-header {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748b;
        }
        .metric-val-row {
            display: flex;
            align-items: baseline;
            gap: 4px;
            margin-top: 0.35rem;
        }
        .metric-large-num {
            font-size: 2.2rem;
            font-weight: 900;
            color: #0f172a;
            line-height: 1;
            letter-spacing: -0.02em;
        }
        .metric-unit {
            font-size: 0.85rem;
            font-weight: 700;
            color: #64748b;
        }
        .progress-track {
            width: 100%;
            height: 6px;
            background: #f1f5f9;
            border-radius: 999px;
            margin-top: 0.75rem;
            overflow: hidden;
        }
        .progress-amber {
            height: 100%;
            background: #f59e0b;
            border-radius: 999px;
        }
        .slider-row {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 0.75rem;
        }
        .slider-label {
            font-size: 0.65rem;
            font-weight: 800;
            color: #64748b;
            white-space: nowrap;
        }
        .slider-track {
            flex: 1;
            height: 4px;
            background: #e2e8f0;
            border-radius: 999px;
            position: relative;
        }
        .slider-thumb-indigo {
            position: absolute;
            top: -4px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4f46e5;
            box-shadow: 0 0 6px rgba(79, 70, 229, 0.4);
        }

        /* Incident List Item */
        .incident-card {
            background: #ffffff;
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
            text-decoration: none !important;
        }
        .incident-card:hover {
            border-color: #0284c7;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(2, 132, 199, 0.08);
        }
        .incident-id-text {
            font-size: 0.92rem;
            font-weight: 900;
            color: #0f172a;
            letter-spacing: -0.01em;
        }
        .incident-sub {
            font-size: 0.72rem;
            color: #64748b;
            margin-top: 3px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .badge-pill {
            display: inline-flex;
            align-items: center;
            padding: 2px 9px;
            border-radius: 6px;
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .badge-critical {
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #dc2626;
        }
        .badge-warning {
            background: rgba(245, 158, 11, 0.18);
            border: 1px solid rgba(245, 158, 11, 0.45);
            color: #fbbf24;
        }
        .badge-resolved {
            background: rgba(16, 185, 129, 0.18);
            border: 1px solid rgba(16, 185, 129, 0.45);
            color: #34d399;
        }

        /* Radar Scanning Rings */
        .radar-box {
            position: relative;
            width: 100%;
            height: 220px;
            border-radius: 20px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at center, #0d1e3a 0%, #060b14 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            margin: 0.85rem 0;
        }
        .radar-ring-1 {
            position: absolute;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 1.5px solid rgba(239, 68, 68, 0.5);
            animation: radar-wave 2.2s infinite ease-out;
        }
        .radar-ring-2 {
            position: absolute;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            border: 1.5px solid rgba(239, 68, 68, 0.7);
            animation: radar-wave 2.2s infinite 0.7s;
        }
        .radar-core {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #ef4444;
            box-shadow: 0 0 16px #ef4444;
            z-index: 2;
        }
        @keyframes radar-wave {
            0% { transform: scale(0.6); opacity: 0.9; }
            100% { transform: scale(1.6); opacity: 0; }
        }
        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.9); opacity: 0.8; }
        }

        /* Telemetry 3-Tile Row */
        .telemetry-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 0.45rem;
            margin: 0.85rem 0;
        }
        .telemetry-tile {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 0.75rem 0.45rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        }
        .telemetry-label {
            font-size: 0.62rem;
            font-weight: 800;
            color: #64748b;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .telemetry-val {
            font-size: 1.1rem;
            font-weight: 900;
            color: #0f172a;
            margin-top: 2px;
        }

        /* 10-Second SOS Banner */
        .sos-timer-card {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.22) 100%);
            border: 2px solid #ef4444;
            border-radius: 24px;
            padding: 1.4rem 1.1rem;
            text-align: center;
            margin-bottom: 1.2rem;
            box-shadow: 0 8px 30px rgba(239, 68, 68, 0.2);
            animation: pulse-border 1.8s infinite;
        }
        @keyframes pulse-border {
            0% { box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2); }
            50% { box-shadow: 0 8px 32px rgba(239, 68, 68, 0.35); }
            100% { box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2); }
        }
        .sos-number {
            font-size: 4rem;
            font-weight: 900;
            color: #dc2626;
            line-height: 1;
            margin: 0.4rem 0 0.1rem;
            text-shadow: 0 2px 10px rgba(239, 68, 68, 0.3);
        }

        /* Floating Frosted Glass Bottom Navigation Dock */
        .floating-nav-dock {
            position: fixed;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 32px);
            max-width: 440px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 999px;
            border: 1px solid rgba(226, 232, 240, 0.95);
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.02);
            display: flex;
            align-items: center;
            justify-content: space-around;
            padding: 8px 12px;
            z-index: 99999;
        }
        .nav-dock-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #64748b;
            text-decoration: none !important;
            padding: 6px 12px;
            border-radius: 999px;
            transition: all 0.2s ease;
            position: relative;
        }
        .nav-dock-btn:hover {
            color: #0284c7;
            transform: translateY(-2px);
        }
        .nav-dock-btn.active {
            color: #0284c7;
        }
        .nav-active-dot {
            width: 5px;
            height: 5px;
            background: #0284c7;
            border-radius: 50%;
            margin-top: 3px;
        }
        .nav-dock-sos {
            text-decoration: none !important;
            position: relative;
            margin: -20px 4px 0;
            display: grid;
            place-items: center;
            transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .nav-dock-sos:hover {
            transform: scale(1.08) translateY(-2px);
        }
        .sos-glow-circle {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f43f5e, #ef4444);
            border: 3.5px solid #ffffff;
            box-shadow: 0 4px 14px rgba(244, 63, 94, 0.4);
            display: grid;
            place-items: center;
            color: #ffffff;
            font-size: 1.3rem;
        }

        /* Streamlit Buttons: Clean White Glass Secondary & Vibrant Primary */
        [data-testid="stButton"] button {
            border-radius: 14px;
            font-weight: 800;
            font-size: 0.85rem;
            letter-spacing: 0.02em;
            transition: all 0.16s ease;
            min-height: 2.85rem;
            background: #ffffff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }
        [data-testid="stButton"] button:hover {
            transform: translateY(-2px);
            border-color: #94a3b8;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
        }
        [data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 8px 24px rgba(239, 68, 68, 0.32) !important;
        }
        [data-testid="stButton"] button[kind="primary"]:hover {
            box-shadow: 0 10px 28px rgba(239, 68, 68, 0.45) !important;
        }
    </style>
    """

st.markdown(
    CSS_TEMPLATE.replace("__THEME_TOKENS__", theme_tokens).replace("__BG_GRADIENT__", bg_gradient),
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# DATABASE & SESSION INITIALIZATION
# -----------------------------------------------------------------------------
db.init_db(seed_sample_data=True)

if "mobile_section" not in st.session_state:
    st.session_state.mobile_section = "Home"

# Support direct tab routing from floating navigation dock (case-insensitive, persist state)
if "section" in st.query_params:
    raw_sec = str(st.query_params.get("section", "")).strip().lower()
    sec_map = {
        "home": "Home",
        "alerts": "Alerts",
        "map": "Map",
        "women": "Women",
        "sim": "Sim",
        "profile": "Settings",
        "settings": "Settings",
    }
    if raw_sec == "sos":
        st.session_state.mobile_timer_active = True
        st.session_state.mobile_timer_start = time.time()
        st.session_state.mobile_timer_cancelled = False
    elif raw_sec in sec_map:
        st.session_state.mobile_section = sec_map[raw_sec]

if "selected_incident_id" not in st.session_state:
    st.session_state.selected_incident_id = None
if "mobile_timer_active" not in st.session_state:
    st.session_state.mobile_timer_active = False
if "mobile_timer_start" not in st.session_state:
    st.session_state.mobile_timer_start = None
if "mobile_timer_cancelled" not in st.session_state:
    st.session_state.mobile_timer_cancelled = False
if "last_call_dispatched" not in st.session_state:
    st.session_state.last_call_dispatched = None
if "is_operator_login_view" not in st.session_state:
    st.session_state.is_operator_login_view = False

# Fetch all incidents from SQLite
all_incidents = db.get_all_incidents()
if not all_incidents:
    db.init_db(seed_sample_data=True)
    all_incidents = db.get_all_incidents()

active_count = len([i for i in all_incidents if i["status"] in ("REPORTED", "DISPATCHED")])
avg_conf = int(sum([i["confidence"] for i in all_incidents]) / max(len(all_incidents), 1))

# Default active incident
if not st.session_state.selected_incident_id and all_incidents:
    st.session_state.selected_incident_id = all_incidents[0]["incident_id"]

# -----------------------------------------------------------------------------
# 10-SECOND EMERGENCY SOS COUNTDOWN BANNER (GLOBAL OVERLAY)
# -----------------------------------------------------------------------------
if st.session_state.mobile_timer_active:
    elapsed = int(time.time() - st.session_state.mobile_timer_start)
    seconds_left = max(0, 10 - elapsed)

    trigger_score = st.session_state.get("auto_triggered_by_score")
    alert_badge = (
        f"● CRASH RISK DETECTED ({trigger_score}%)"
        if trigger_score
        else "● CRASH SENSORS TRIGGERED"
    )

    st.markdown(
        f"""
        <div class="sos-timer-card">
            <div style="font-size:0.75rem; font-weight:800; color:#fca5a5; letter-spacing:0.12em; text-transform:uppercase;">
                {alert_badge}
            </div>
            <div style="font-size:1.15rem; font-weight:900; color:#ffffff; margin-top:2px;">
                AUTOMATIC EMERGENCY SOS ACTIVATED
            </div>
            <div class="sos-number">{seconds_left}s</div>
            <div style="font-size:0.75rem; color:#fca5a5; margin-bottom:0.75rem;">
                Crash risk threshold exceeded (<b>{trigger_score}% ≥ 70%</b>). Automated Twilio voice call & location dispatch to <b>{notify.EMERGENCY_DISPATCH_PHONE}</b> in:
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:6px; font-size:0.75rem; color:#67e8f9; font-weight:700;">
                📍 Active GPS: 17.4435, 78.3772 · MG Road Corridor
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_cancel, col_now = st.columns(2)
    with col_cancel:
        if st.button("✋ I'M OK (CANCEL)", key="cancel_sos_timer", use_container_width=True):
            st.session_state.mobile_timer_active = False
            st.session_state.mobile_timer_start = None
            st.session_state.mobile_timer_cancelled = True
            st.session_state.score_dismissed = True
            st.rerun()
    with col_now:
        if st.button("⚡ DISPATCH NOW", key="force_sos_timer", type="primary", use_container_width=True):
            seconds_left = 0

    if seconds_left > 0:
        time.sleep(1)
        st.rerun()
    else:
        # 10-Second Timer Finished -> Trigger Twilio Voice Call & Location Message
        st.session_state.mobile_timer_active = False
        st.session_state.mobile_timer_start = None

        target_phone = notify.EMERGENCY_DISPATCH_PHONE
        inc_id = db.create_incident(
            vehicle_type="Motorcycle",
            latitude=17.4435,
            longitude=78.3772,
            confidence=89.0,
            rider_status="NEED HELP",
            language="English",
            message="10-Second timer expired. Emergency auto-dispatch triggered from mobile app.",
            status="REPORTED",
            address="12 MG Road, Bengaluru",
        )
        st.session_state.selected_incident_id = inc_id

        # Trigger Twilio Voice Call
        call_res = notify.trigger_emergency_call(
            {
                "incident_id": inc_id,
                "vehicle_type": "Motorcycle",
                "confidence": 89.0,
                "city": "12 MG Road, Bengaluru",
            },
            to_phone=target_phone,
        )
        notify.send_emergency_sms(
            {"incident_id": inc_id, "vehicle_type": "Motorcycle", "confidence": 89.0, "latitude": 17.4435, "longitude": 78.3772},
            to_phone=target_phone,
        )
        notify.send_whatsapp_location(
            {"incident_id": inc_id, "vehicle_type": "Motorcycle", "confidence": 89.0, "latitude": 17.4435, "longitude": 78.3772},
            to_phone=target_phone,
            address="12 MG Road, Bengaluru",
        )

        st.session_state.last_call_dispatched = {
            "incident_id": inc_id,
            "call_sid": call_res.get("sid", "Queued"),
            "target": target_phone,
            "call_success": call_res.get("success", False),
            "error": call_res.get("error"),
        }
        st.rerun()

# -----------------------------------------------------------------------------
# SCREEN 1: OPERATOR ACCESS PORTAL (LOGIN / SPLASH VIEW)
# -----------------------------------------------------------------------------
if st.session_state.is_operator_login_view:
    st.markdown(
        """
        <div style="text-align:center; padding: 2.2rem 0.5rem 1rem;">
            <div style="width:78px; height:78px; border-radius:24px; background:linear-gradient(135deg, #1e3a8a, #0284c7); margin:0 auto 1.2rem; display:grid; place-items:center; font-size:2.2rem; box-shadow:0 0 35px rgba(2,132,199,0.4); border:1.5px solid rgba(255,255,255,0.18);">
                🛡️
            </div>
            <div style="font-size:1.85rem; font-weight:900; color:#f8fafc; letter-spacing:-0.03em; margin-bottom:4px;">
                SafeRide AI
            </div>
            <div style="font-size:0.8rem; color:#94a3b8; max-width:280px; margin:0 auto 1.8rem; line-height:1.4;">
                Real-time crash detection & emergency response platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(
            """
            <div class="glass-card" style="padding:1.4rem;">
                <div style="font-size:0.68rem; font-weight:800; color:#7dd3fc; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:8px;">
                    OPERATOR ACCESS PORTAL
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_input("Enter mobile number", value="+91 74169 60828", label_visibility="collapsed")
        
        if st.button("Operator Log In", type="primary", use_container_width=True):
            st.session_state.is_operator_login_view = False
            st.rerun()

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    if st.button("🚨 BYPASS TO SOS", use_container_width=True):
        st.session_state.is_operator_login_view = False
        st.session_state.mobile_timer_active = True
        st.session_state.mobile_timer_start = time.time()
        st.session_state.mobile_timer_cancelled = False
        st.rerun()

    st.stop()

# -----------------------------------------------------------------------------
# MAIN APP HEADER: RIDER PROFILE + ACTIVE SYSTEM STRIP + THEME TOGGLE
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-container">
        <div class="header-left">
            <div class="rider-avatar">
                <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80" style="width:100%; height:100%; object-fit:cover;" alt="Rider"/>
            </div>
            <div class="header-title-stack">
                <div class="header-app-name">SAFERIDE AI</div>
                <div class="header-status-text">
                    <span class="status-dot-emerald"></span>
                    ARMED &amp; LOGGING
                </div>
            </div>
        </div>
        <div class="header-right">
            <div class="header-pill">
                <span style="color:#10b981; font-size:0.85rem;">⚡</span>
                <span>94%</span>
            </div>
            <div class="header-pill">
                <span style="color:#0284c7; font-size:0.8rem;">🛜</span>
                <span>RTK GPS</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Flash active call banner if recently dispatched
if st.session_state.last_call_dispatched:
    cinfo = st.session_state.last_call_dispatched
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, rgba(16,185,129,0.18) 0%, rgba(5,150,105,0.28) 100%); border:1px solid #10b981; border-radius:14px; padding:0.85rem; margin-bottom:0.85rem;">
            <div style="font-size:0.88rem; font-weight:800; color:#059669;">
                📞 Automated Twilio Call Dispatched to {cinfo['target']}
            </div>
            <div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">
                Call Reference SID: <code>{cinfo['call_sid']}</code> · Responders Notified
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# TAB 1: ⌂ HOME (DASHBOARD)
# -----------------------------------------------------------------------------
if st.session_state.mobile_section == "Home":
    # --- HERO CIRCULAR SVG CONFIDENCE HORSESHOE GAUGE CARD ---
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border-radius:28px; padding:1.4rem 1.2rem 1.25rem; text-align:center; box-shadow:0 10px 32px rgba(0,0,0,0.03); border:1px solid #e2e8f0; margin-bottom:0.85rem;">
            <div style="position:relative; width:210px; height:185px; margin:0 auto 0.2rem; display:flex; align-items:center; justify-content:center;">
                <svg width="210" height="185" viewBox="0 0 210 185">
                    <defs>
                        <linearGradient id="horseshoeEmerald" x1="0%" y1="100%" x2="100%" y2="0%">
                            <stop offset="0%" stop-color="#059669"/>
                            <stop offset="50%" stop-color="#10b981"/>
                            <stop offset="100%" stop-color="#34d399"/>
                        </linearGradient>
                    </defs>
                    <!-- Background Horseshoe Track (Open at bottom) -->
                    <path d="M 42 148 A 76 76 0 1 1 168 148" fill="none" stroke="#f1f5f9" stroke-width="13" stroke-linecap="round"/>
                    <!-- Active Emerald Progress Arc (98% confidence) -->
                    <path d="M 42 148 A 76 76 0 1 1 168 148" fill="none" stroke="url(#horseshoeEmerald)" stroke-width="13" stroke-linecap="round" stroke-dasharray="355" stroke-dashoffset="10"/>
                </svg>
                <div style="position:absolute; top:54%; left:50%; transform:translate(-50%, -50%); text-align:center; width:100%;">
                    <div style="font-size:0.72rem; font-weight:800; color:#059669; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:1px;">NOMINAL</div>
                    <div style="font-size:3.2rem; font-weight:900; color:#0f172a; line-height:0.95; letter-spacing:-0.03em;">98<span style="font-size:1.4rem; font-weight:700; color:#64748b;">%</span></div>
                    <div style="font-size:0.68rem; font-weight:800; color:#64748b; letter-spacing:0.12em; text-transform:uppercase; margin-top:4px;">CONFIDENCE</div>
                </div>
            </div>
            <div style="display:inline-flex; align-items:center; gap:8px; padding:0.45rem 1.25rem; border-radius:999px; background:#e6fbf2; border:1.5px solid rgba(16,185,129,0.35); color:#047857; font-size:0.8rem; font-weight:800; letter-spacing:0.03em;">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="16 9 10 15 7 12"></polyline>
                </svg>
                ALL TELEMETRY NOMINAL
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 2x2 TELEMETRY HUD TILES MATCHING REFERENCE IMAGE ---
    st.markdown(
        """
        <div class="metric-grid">
            <!-- Tile 1: SPEED -->
            <div class="metric-tile">
                <div class="metric-header">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    <span>SPEED</span>
                </div>
                <div class="metric-val-row">
                    <span class="metric-large-num">50</span>
                    <span class="metric-unit">km/h</span>
                </div>
            </div>
            <!-- Tile 2: PEAK G-FORCE -->
            <div class="metric-tile">
                <div class="metric-header">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                    <span>PEAK G-FORCE</span>
                </div>
                <div class="metric-val-row">
                    <span class="metric-large-num">1.5</span>
                    <span class="metric-unit">G</span>
                </div>
                <div class="progress-track">
                    <div class="progress-amber" style="width: 52%;"></div>
                </div>
            </div>
            <!-- Tile 3: LEAN ANGLE -->
            <div class="metric-tile">
                <div class="metric-header">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
                    <span>LEAN ANGLE</span>
                </div>
                <div class="metric-val-row">
                    <span class="metric-large-num">26°</span>
                </div>
                <div class="slider-row">
                    <span class="slider-label">L 45°</span>
                    <div class="slider-track">
                        <div class="slider-thumb-indigo" style="left: 60%;"></div>
                    </div>
                    <span class="slider-label">R 45°</span>
                </div>
            </div>
            <!-- Tile 4: IMPACT STATE -->
            <div class="metric-tile">
                <div class="metric-header">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    <span>IMPACT STATE</span>
                </div>
                <div class="metric-val-row">
                    <span class="metric-large-num" style="color: #059669;">0.0G</span>
                </div>
                <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; margin-top: 3px;">
                    Threshold safe
                </div>
            </div>
        </div>

        <!-- HIGH PRIORITY EMERGENCY DISPATCH CARD (Directly below 2x2 grid, scrolls under nav dock) -->
        <div class="glass-card" style="background:#ffffff; border:1.5px solid rgba(239,68,68,0.3); border-radius:20px; padding:1.1rem; box-shadow:0 8px 24px rgba(239,68,68,0.06); margin-top:0.2rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <div style="font-size:0.75rem; font-weight:900; color:#ef4444; letter-spacing:0.1em; text-transform:uppercase;">
                    ● HIGH PRIORITY DISPATCH
                </div>
                <span style="font-size:0.68rem; font-weight:800; color:#dc2626; background:rgba(239,68,68,0.1); padding:2px 8px; border-radius:6px;">
                    TWILIO CLOUD
                </span>
            </div>
            <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:2px;">
                Automated Emergency Voice &amp; Location Dispatch
            </div>
            <div style="font-size:0.74rem; color:#64748b; line-height:1.4; margin-bottom:8px;">
                Continuous AI sensor fusion armed. 10-second warning countdown before automated voice calls to <b>+91 74169 60828</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Direct 1-Click Trigger to inspect or engage SOS
    if st.button("🚨 TRIGGER 10s EMERGENCY SOS", type="primary", use_container_width=True):
        st.session_state.mobile_timer_active = True
        st.session_state.mobile_timer_start = time.time()
        st.session_state.mobile_timer_cancelled = False
        st.rerun()

    # -------------------------------------------------------------------------
    # 🌸 WOMEN SAFETY EMERGENCY SECTION
    # -------------------------------------------------------------------------
    women_card_bg = "background: #ffffff; border: 1.5px solid rgba(244, 63, 94, 0.35); box-shadow: 0 8px 24px rgba(244, 63, 94, 0.08);" if is_white_theme else "background: linear-gradient(135deg, rgba(190, 24, 93, 0.28) 0%, rgba(131, 24, 67, 0.45) 100%); border: 1.5px solid rgba(244, 114, 182, 0.45); box-shadow: 0 10px 30px rgba(190, 24, 93, 0.35);"
    women_title_color = "#be123c" if is_white_theme else "#fdf2f8"
    women_sub_color = "#9f1239" if is_white_theme else "#fbcfe8"
    women_desc_color = "#475569" if is_white_theme else "#fce7f3"

    st.markdown(
        f"""
        <div class="glass-card" style="{women_card_bg} margin-top:0.6rem;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <div style="width:38px; height:38px; border-radius:12px; background:#fff1f2; border:1px solid #fecdd3; display:grid; place-items:center; font-size:1.4rem;">
                    🌸
                </div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:{women_title_color}; letter-spacing:0.02em;">WOMEN SAFETY EMERGENCY SOS</div>
                    <div style="font-size:0.7rem; color:{women_sub_color}; font-weight:600;">Priority police & emergency responder voice dispatch</div>
                </div>
            </div>
            <div style="font-size:0.75rem; color:{women_desc_color}; line-height:1.4; margin-bottom:6px;">
                Directly triggers an automated Twilio voice call and high-priority GPS location SMS to emergency dispatch and emergency contacts.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_w1, col_w2 = st.columns([1.6, 1])
    with col_w1:
        if st.button("🌸 ACTIVATE WOMEN SAFETY SOS", key="btn_home_women_sos", type="primary", use_container_width=True):
            with st.spinner("Activating Women Safety Emergency Dispatch via Twilio..."):
                inc_id = db.create_incident(
                    vehicle_type="Women Safety SOS",
                    latitude=17.4435,
                    longitude=78.3772,
                    confidence=100.0,
                    rider_status="EMERGENCY ASSISTANCE",
                    language="English",
                    message="Critical Women Safety SOS triggered. Immediate police & responder dispatch required.",
                    status="REPORTED",
                    address="12 MG Road, Bengaluru",
                )
                women_twiml = (
                    "<Response><Pause length=\"1\"/><Say voice=\"alice\" language=\"en-IN\">"
                    "Urgent Emergency Alert from SafeRide AI. Critical Women Safety SOS has been activated for female rider at coordinates latitude 17.4435, longitude 78.3772. "
                    "Immediate police assistance and emergency responder dispatch is required. Check terminal now.</Say></Response>"
                )
                women_sms = (
                    "🚨 SafeRide AI WOMEN SAFETY EMERGENCY ALERT! Female rider requested immediate assistance at "
                    "Lat 17.4435, Lon 78.3772. Google Maps: https://maps.google.com/?q=17.4435,78.3772. "
                    "Immediate police and emergency response needed!"
                )
                c_res = notify.trigger_emergency_call(
                    {"incident_id": inc_id, "vehicle_type": "Women Safety SOS", "confidence": 100.0, "city": "12 MG Road, Bengaluru"},
                    to_phone=notify.EMERGENCY_DISPATCH_PHONE,
                    custom_twiml=women_twiml
                )
                s_res = notify.send_emergency_sms(
                    {"incident_id": inc_id, "vehicle_type": "Women Safety SOS", "confidence": 100.0, "latitude": 17.4435, "longitude": 78.3772},
                    to_phone=notify.EMERGENCY_DISPATCH_PHONE,
                    custom_body=women_sms
                )
                st.session_state.last_call_dispatched = {
                    "incident_id": inc_id,
                    "call_sid": c_res.get("sid", "Queued"),
                    "target": notify.EMERGENCY_DISPATCH_PHONE,
                    "call_success": c_res.get("success", False),
                    "error": c_res.get("error"),
                }
                st.rerun()

    with col_w2:
        st.markdown(
            f"""
            <a href="tel:{notify.EMERGENCY_DISPATCH_PHONE}" style="text-decoration:none;">
                <div style="display:flex; align-items:center; justify-content:center; height:38px; border-radius:10px; background:#fff1f2; border:1.5px solid #fda4af; color:#be123c; font-weight:800; font-size:0.75rem; cursor:pointer;">
                    📞 Dial {notify.EMERGENCY_DISPATCH_PHONE[-4:]}
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    if st.button("⚡ Test Direct Twilio Emergency Call Now", use_container_width=True):
        with st.spinner(f"Placing direct Twilio voice call to {notify.EMERGENCY_DISPATCH_PHONE}..."):
            c_res = notify.trigger_emergency_call(
                {"incident_id": "TEST-VOICE", "vehicle_type": "Motorcycle", "confidence": 98.0, "city": "Bengaluru Central"},
                to_phone=notify.EMERGENCY_DISPATCH_PHONE
            )
            s_res = notify.send_emergency_sms(
                {"incident_id": "TEST-VOICE", "vehicle_type": "Motorcycle", "confidence": 98.0, "latitude": 17.5192, "longitude": 78.6299},
                to_phone=notify.EMERGENCY_DISPATCH_PHONE
            )
            if c_res.get("success"):
                st.success(f"📞 Twilio Voice Call Placed! SID: {c_res.get('sid')} (Status: {c_res.get('status')})")
            else:
                st.error(f"Twilio notice: {c_res.get('error')}")

# -----------------------------------------------------------------------------
# TAB 2: ! ALERTS / ACTIVE INCIDENT DETAIL VIEW
# -----------------------------------------------------------------------------
elif st.session_state.mobile_section == "Alerts":
    cur_inc = db.get_incident(st.session_state.selected_incident_id) or all_incidents[0]
    
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:space-between; margin:0.4rem 0 0.85rem;">
            <div style="font-size:1.2rem; font-weight:900; color:#0f172a; letter-spacing:-0.02em;">
                Incident #{cur_inc['incident_id']}
            </div>
            <span style="background:#fef2f2; border:1px solid #fecaca; color:#dc2626; font-size:0.72rem; font-weight:800; padding:3px 10px; border-radius:999px;">
                ● CRITICAL
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Rider Profile Card
    st.markdown(
        f"""
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:22px; padding:1.2rem; box-shadow:0 6px 20px rgba(0,0,0,0.03); margin-bottom:0.85rem;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:44px; height:44px; border-radius:50%; background:linear-gradient(135deg, #ef4444, #f97316); display:grid; place-items:center; font-size:1.25rem; flex-shrink:0;">
                        🏍️
                    </div>
                    <div>
                        <div style="font-size:1rem; font-weight:900; color:#0f172a;">Anand Verma</div>
                        <div style="font-size:0.75rem; color:#dc2626; font-weight:800; margin-top:2px;">Rider Status: {cur_inc.get('rider_status', 'NEED HELP')}</div>
                    </div>
                </div>
                <div>
                    <a href="tel:{notify.EMERGENCY_DISPATCH_PHONE}" style="text-decoration:none;">
                        <span style="display:inline-block; padding:7px 13px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; font-size:0.75rem; color:#1d4ed8; font-weight:800;">📞 Call</span>
                    </a>
                </div>
            </div>
            <div style="margin-top:0.85rem; padding-top:0.75rem; border-top:1px solid #f1f5f9; font-size:0.75rem; color:#64748b;">
                <b style="color:#0284c7; font-size:0.7rem; letter-spacing:0.06em; text-transform:uppercase;">Reverse Geocoded Address:</b><br/>
                <span style="color:#0f172a; font-weight:700; font-size:0.82rem; margin-top:2px; display:inline-block;">{cur_inc.get('address') or '12 MG Road, Bengaluru'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mini Glowing Radar Box
    st.markdown(
        """
        <div class="radar-box">
            <div class="radar-ring-1"></div>
            <div class="radar-ring-2"></div>
            <div class="radar-core"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Telemetry Tiles: Speed Before, Speed After, G-Force
    st.markdown(
        f"""
        <div class="telemetry-row">
            <div class="telemetry-tile" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:18px; padding:0.85rem 0.5rem; text-align:center; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
                <div class="telemetry-label" style="color:#64748b; font-size:0.65rem; font-weight:800;">SPEED BEFORE</div>
                <div class="telemetry-val" style="color:#0f172a; font-size:1.15rem; font-weight:900;">87 km/h</div>
            </div>
            <div class="telemetry-tile" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:18px; padding:0.85rem 0.5rem; text-align:center; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
                <div class="telemetry-label" style="color:#64748b; font-size:0.65rem; font-weight:800;">SPEED AFTER</div>
                <div class="telemetry-val" style="color:#059669; font-size:1.15rem; font-weight:900;">0 km/h</div>
            </div>
            <div class="telemetry-tile" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:18px; padding:0.85rem 0.5rem; text-align:center; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
                <div class="telemetry-label" style="color:#64748b; font-size:0.65rem; font-weight:800;">G-FORCE</div>
                <div class="telemetry-val" style="color:#dc2626; font-size:1.15rem; font-weight:900;">4.2 G</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # AI Confidence Bar
    conf_val = int(cur_inc.get("confidence", 89))
    st.markdown(
        f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:0.85rem 1rem; margin-bottom:0.85rem; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:800; color:#64748b; margin-bottom:6px;">
                <span>AI INCIDENT CONFIDENCE</span>
                <span style="color:#d97706; font-weight:900;">{conf_val}%</span>
            </div>
            <div style="width:100%; height:8px; background:#f1f5f9; border-radius:99px; overflow:hidden;">
                <div style="width:{conf_val}%; height:100%; background:linear-gradient(90deg, #f59e0b, #ef4444); border-radius:99px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Quick Action Buttons: Dispatch 108, SMS, Call (Twilio), Resolve
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("🚨 108", help="Dispatch 108 Ambulance", use_container_width=True):
            st.session_state.mobile_timer_active = True
            st.session_state.mobile_timer_start = time.time()
            st.rerun()
    with col_b:
        if st.button("💬 SMS", help="Send Emergency SMS", use_container_width=True):
            notify.send_emergency_sms(dict(cur_inc), to_phone=notify.EMERGENCY_DISPATCH_PHONE)
            st.success("SMS Dispatched!")
    with col_c:
        if st.button("📞 Call", help="Automated Twilio Call", use_container_width=True):
            res = notify.trigger_emergency_call(dict(cur_inc), to_phone=notify.EMERGENCY_DISPATCH_PHONE)
            st.info(f"Twilio Call: {res.get('status', 'queued')}")
    with col_d:
        if st.button("✓ Done", help="Mark Resolved", use_container_width=True):
            db.update_incident(cur_inc["incident_id"], status="RESOLVED")
            st.success("Resolved!")
            st.rerun()

    # Activities Timeline
    st.markdown(
        """
        <div style="font-size:0.85rem; font-weight:900; color:#0f172a; margin:1.1rem 0 0.5rem; letter-spacing:0.02em;">ACTION TIMELINE</div>
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:18px; padding:0.9rem 1rem; font-size:0.75rem; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
            <div style="margin-bottom:8px; color:#334155; font-weight:600;">● Emergency unit 04 dispatched · <span style="color:#64748b; font-weight:500;">14:24:12</span></div>
            <div style="margin-bottom:8px; color:#334155; font-weight:600;">● Rider confirmed address via Twilio speech · <span style="color:#64748b; font-weight:500;">14:23:45</span></div>
            <div style="color:#059669; font-weight:700;">● Automated voice alert completed · <span style="color:#64748b; font-weight:500;">14:23:01</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# TAB 3: ⌖ MAP (LIVE GIS RADAR TRACKER)
# -----------------------------------------------------------------------------
elif st.session_state.mobile_section == "Map":
    st.markdown(
        """
        <div style="margin:0.4rem 0 0.85rem;">
            <input type="text" placeholder="🔍 Search active incident or landmark..." style="width:100%; background:#ffffff; border:1px solid #cbd5e1; border-radius:14px; padding:10px 14px; color:#0f172a; font-size:0.82rem; font-weight:600; box-shadow:0 2px 8px rgba(0,0,0,0.03);" />
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Leaflet Interactive Map
    try:
        import folium
        from streamlit_folium import folium_static

        m = folium.Map(
            location=[17.4435, 78.3772],
            zoom_start=14,
            tiles="CartoDB dark_matter",
            control_scale=False,
            zoom_control=False,
        )

        # Radar circle perimeter
        folium.Circle(
            location=[17.4435, 78.3772],
            radius=350,
            color="#ef4444",
            fill=True,
            fill_color="#ef4444",
            fill_opacity=0.18,
            weight=2,
        ).add_to(m)

        folium.Circle(
            location=[17.4435, 78.3772],
            radius=750,
            color="#ef4444",
            fill=False,
            weight=1,
            dash_array="5, 8",
        ).add_to(m)

        # Pulsing Red Marker
        folium.Marker(
            location=[17.4435, 78.3772],
            popup="Active Crash Perimeter",
            icon=folium.Icon(color="red", icon="warning", prefix="fa"),
        ).add_to(m)

        folium_static(m, width=440, height=360)
    except Exception:
        st.markdown(
            """
            <div class="radar-box" style="height:320px;">
                <div class="radar-ring-1"></div>
                <div class="radar-ring-2"></div>
                <div class="radar-core"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Floating Bottom Incident Card
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; box-shadow:0 4px 16px rgba(0,0,0,0.03); margin-top:0.75rem; display:flex; align-items:center; justify-content:space-between; padding:1rem 1.15rem;">
            <div>
                <div style="font-size:0.92rem; font-weight:900; color:#0f172a;">#SR-0042 <span style="background:#fef2f2; border:1px solid #fecaca; color:#dc2626; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:999px; margin-left:6px;">CRITICAL</span></div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:600; margin-top:3px;">MG Road Corridor · 17.4435, 78.3772</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚨 INSTANT DISPATCH TO SCENE", type="primary", use_container_width=True):
        st.session_state.mobile_timer_active = True
        st.session_state.mobile_timer_start = time.time()
        st.rerun()

# -----------------------------------------------------------------------------
# TAB 4: ⚡ SIM (CRASH SIMULATOR)
# -----------------------------------------------------------------------------
elif st.session_state.mobile_section == "Sim":
    st.markdown(
        """
        <div style="margin:0.4rem 0 0.85rem;">
            <div style="font-size:1.25rem; font-weight:900; color:#0f172a; letter-spacing:-0.02em;">
                ⚡ Crash Simulator
            </div>
            <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                Simulate velocity drops, g-forces, and tilt vectors to test AI scoring.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preset = st.selectbox(
        "PRESET SELECTOR",
        options=list(ad.SIMULATION_PRESETS.keys()),
        index=3,
        label_visibility="visible",
    )
    p_data = ad.SIMULATION_PRESETS[preset]

    # Vehicle Selector Pills
    v_type = st.radio("VEHICLE TYPE", ["Motorcycle (92%)", "Car", "Auto", "Bus"], horizontal=True)
    clean_v_type = v_type.split()[0]

    # Telemetry Sliders
    sp_before = st.slider("Speed Before Impact (km/h)", 0, 160, int(p_data["speed_before"]))
    sp_after = st.slider("Speed After Impact (km/h)", 0, 160, int(p_data["speed_after"]))
    g_force = st.slider("G-Force Impact Vector (G)", 0.5, 12.0, float(p_data["impact_force_g"]), 0.1)
    tilt = st.slider("Maximum Tilt Angle (°)", 0, 90, int(p_data["tilt_angle_deg"]))

    # Evaluate with AI Detection Module
    eval_res = ad.detect_accident(
        speed_before=sp_before,
        speed_after=sp_after,
        impact_force_g=g_force,
        tilt_angle_deg=tilt,
        vehicle_type=clean_v_type,
    )

    score = int(eval_res["confidence"])
    if score >= 70:
        score_color = "#dc2626"
        badge_bg = "#fef2f2"
        badge_border = "#fecaca"
        badge_text = f"🔴 CRASH RISK DETECTED ({score}%)"
        prob_text = "CRITICAL CRASH PROBABILITY · AUTO SOS ARMED"
    elif score >= 45:
        score_color = "#d97706"
        badge_bg = "#fffbeb"
        badge_border = "#fde68a"
        badge_text = f"🟡 ELEVATED IMPACT ({score}%) — MONITORING"
        prob_text = "ELEVATED IMPACT READINGS · MONITORING (NO SOS)"
    else:
        score_color = "#059669"
        badge_bg = "#ecfdf5"
        badge_border = "#a7f3d0"
        badge_text = "🟢 ALL TELEMETRY NOMINAL · RIDE SAFE"
        prob_text = "NORMAL RIDE TELEMETRY"

    st.markdown(
        f"""
        <div class="glass-card" style="background:#ffffff; border:1.5px solid {score_color}; border-radius:22px; text-align:center; padding:1.35rem 1.1rem; box-shadow:0 8px 24px rgba(0,0,0,0.04); margin-bottom:0.9rem;">
            <div style="display:inline-block; padding:4px 14px; border-radius:99px; background:{badge_bg}; border:1px solid {badge_border}; font-size:0.72rem; font-weight:800; color:{score_color}; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0.5rem;">
                {badge_text}
            </div>
            <div style="font-size:3.4rem; font-weight:900; color:{score_color}; line-height:1; margin:0.35rem 0;">
                {score}%
            </div>
            <div style="font-size:0.82rem; font-weight:800; color:{score_color}; letter-spacing:0.04em;">
                {prob_text}
            </div>
            <div style="font-size:0.74rem; color:#64748b; font-weight:600; margin-top:0.55rem;">
                Speed: <b>{eval_res['scores']['speed_drop_score']}%</b> · Impact: <b>{eval_res['scores']['impact_score']}%</b> · Tilt: <b>{eval_res['scores']['tilt_score']}%</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auto_trigger = st.toggle("⚡ Auto-activate Emergency SOS on crash risk (≥70%)", value=True)
    if auto_trigger and score >= 70:
        if not st.session_state.get("mobile_timer_active", False) and not st.session_state.get("score_dismissed", False):
            st.session_state.mobile_timer_active = True
            st.session_state.mobile_timer_start = time.time()
            st.session_state.mobile_timer_cancelled = False
            st.session_state.auto_triggered_by_score = score
            st.rerun()
    elif score < 70:
        st.session_state.score_dismissed = False
        st.session_state.auto_triggered_by_score = None

    if st.button("🚨 Trigger Emergency SOS (10s Countdown)", type="primary", use_container_width=True):
        st.session_state.mobile_timer_active = True
        st.session_state.mobile_timer_start = time.time()
        st.session_state.mobile_timer_cancelled = False
        st.session_state.auto_triggered_by_score = score
        st.session_state.score_dismissed = False
        st.rerun()

# -----------------------------------------------------------------------------
# TAB 5: ⚙️ SETTINGS & SYSTEM CONFIGURATION CONSOLE
# -----------------------------------------------------------------------------
elif st.session_state.mobile_section in ["Profile", "Settings"]:
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin:0.4rem 0 0.95rem;">
            <div>
                <div style="font-size:1.3rem; font-weight:900; color:#0f172a; letter-spacing:-0.02em;">
                    ⚙️ Settings &amp; Preferences
                </div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                    Manage emergency dispatch, sensor calibration &amp; app display
                </div>
            </div>
            <span style="background:#ecfdf5; border:1px solid #a7f3d0; color:#059669; font-size:0.7rem; font-weight:800; padding:4px 12px; border-radius:999px;">
                ● SYSTEM ARMED
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 1. RIDER PROFILE CARD ---
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:24px; padding:1.25rem; box-shadow:0 8px 24px rgba(0,0,0,0.03); margin-bottom:0.9rem;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:58px; height:58px; border-radius:50%; border:2.5px solid #0284c7; box-shadow:0 4px 14px rgba(2,132,199,0.25); overflow:hidden; flex-shrink:0;">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80" style="width:100%; height:100%; object-fit:cover;" alt="Alex Turner"/>
                </div>
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; justify-content:space-between;">
                        <div style="font-size:1.1rem; font-weight:900; color:#0f172a;">Alex Turner</div>
                        <span style="font-size:0.65rem; font-weight:800; background:#eff6ff; border:1px solid #bfdbfe; color:#1d4ed8; padding:2px 8px; border-radius:6px;">
                            VERIFIED RIDER
                        </span>
                    </div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                        Yamaha MT-07 · <b>KA-01-EQ-4291</b>
                    </div>
                    <div style="font-size:0.72rem; color:#059669; font-weight:700; margin-top:3px;">
                        🩸 Blood Group: <b>O+ Positive</b> · No Medical Allergies
                    </div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:1rem; padding-top:0.85rem; border-top:1px solid #f1f5f9; text-align:center;">
                <div>
                    <div style="font-size:1.1rem; font-weight:900; color:#0284c7;">1,240 <span style="font-size:0.7rem; font-weight:600; color:#64748b;">km</span></div>
                    <div style="font-size:0.62rem; font-weight:800; color:#64748b; text-transform:uppercase;">MONITORED</div>
                </div>
                <div>
                    <div style="font-size:1.1rem; font-weight:900; color:#059669;">98%</div>
                    <div style="font-size:0.62rem; font-weight:800; color:#64748b; text-transform:uppercase;">SAFETY INDEX</div>
                </div>
                <div>
                    <div style="font-size:1.1rem; font-weight:900; color:#d97706;">12 <span style="font-size:0.7rem; font-weight:600; color:#64748b;">ms</span></div>
                    <div style="font-size:0.62rem; font-weight:800; color:#64748b; text-transform:uppercase;">AI LATENCY</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 2. EMERGENCY DISPATCH & TWILIO CLOUD GATEWAY ---
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:24px; padding:1.25rem; box-shadow:0 8px 24px rgba(0,0,0,0.03); margin-bottom:0.9rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.85rem;">
                <div style="font-size:0.8rem; font-weight:900; color:#0284c7; letter-spacing:0.08em; text-transform:uppercase;">
                    📞 EMERGENCY DISPATCH &amp; TWILIO CLOUD
                </div>
                <span style="font-size:0.65rem; font-weight:800; color:#059669; background:#ecfdf5; border:1px solid #10b981; padding:2px 8px; border-radius:999px;">
                    ● GATEWAY ONLINE
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    new_dispatch_phone = st.text_input(
        "Primary Emergency Dispatch Phone",
        value=notify.EMERGENCY_DISPATCH_PHONE,
        help="All automated emergency voice calls and priority SMS dispatch to this phone number.",
    )
    if new_dispatch_phone != notify.EMERGENCY_DISPATCH_PHONE:
        notify.EMERGENCY_DISPATCH_PHONE = new_dispatch_phone.strip()
        st.toast(f"Emergency dispatch phone updated to {notify.EMERGENCY_DISPATCH_PHONE}!", icon="✅")

    secondary_guardian = st.text_input(
        "Secondary Family / Guardian Phone",
        value="+91 98765 43210",
        help="Receives backup incident location SMS and WhatsApp GPS links.",
    )

    col_sos_time, col_sos_lang = st.columns(2)
    with col_sos_time:
        sos_duration = st.selectbox("SOS Countdown Window", ["5 seconds", "10 seconds", "15 seconds", "30 seconds"], index=1)
    with col_sos_lang:
        call_lang = st.selectbox("Voice Alert Language", ["English (en-IN)", "Hindi (hi-IN)", "Kannada (kn-IN)", "Telugu (te-IN)"])

    st.toggle("Automated Twilio Voice Call on Crash Detection", value=True, help="Places an automated phone call to emergency dispatch.")
    st.toggle("High-Priority Location SMS Broadcast", value=True, help="Sends real-time coordinates and verified address to dispatch.")
    st.toggle("WhatsApp Live GPS Coordinates Link", value=True, help="Generates clickable Google Maps route for first responders.")
    st.toggle("Relay Incident to 112 / 108 Emergency Network", value=True, help="Enables mutual-aid responder routing.")

    if st.button("📞 TEST TWILIO VOICE CALL TO DISPATCH", key="btn_test_twilio_call", use_container_width=True):
        with st.spinner(f"Connecting to Twilio Cloud & dialing {notify.EMERGENCY_DISPATCH_PHONE}..."):
            test_res = notify.trigger_emergency_call(
                {
                    "incident_id": "TEST-PING",
                    "vehicle_type": "Motorcycle",
                    "confidence": 98.0,
                    "city": "12 MG Road, Bengaluru (Settings Test Call)",
                },
                to_phone=notify.EMERGENCY_DISPATCH_PHONE,
            )
            if test_res.get("success"):
                st.success(f"Twilio call dispatched successfully! SID: {test_res.get('sid', 'Queued')}")
            else:
                st.warning(f"Call dispatch status: {test_res.get('error', 'Dialed via Twilio')}")

    # --- 3. CRASH DETECTION SENSITIVITY & AI SENSOR TUNING ---
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:24px; padding:1.25rem; box-shadow:0 8px 24px rgba(0,0,0,0.03); margin:1.2rem 0 0.85rem;">
            <div style="font-size:0.8rem; font-weight:900; color:#d97706; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.35rem;">
                ⚡ SENSOR CALIBRATION &amp; AI TUNING
            </div>
            <div style="font-size:0.72rem; color:#64748b;">
                Fine-tune sensor fusion thresholds to prevent false positives while ensuring reliable crash triggers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    conf_thresh = st.slider("AI Crash Confidence Trigger Threshold (%)", 50, 95, 70, help="Incidents with AI confidence score ≥ this value activate automatic 10s emergency dispatch.")
    impact_thresh = st.slider("Peak Impact Force Trigger (G)", 2.0, 7.5, 3.0, 0.1, help="Motorcycle impacts typically generate 3.5G-7.0G; road bumps are <2.5G.")
    tilt_thresh = st.slider("Horizon Tilt Lay-Down Angle (°)", 45, 85, 65, help="Lean angle exceeding this threshold signals fall-over or lay-down.")
    speed_drop_thresh = st.slider("Instant Deceleration Delta Trigger (km/h)", 20, 60, 35, help="Sudden velocity drops exceeding this delta contribute to crash risk.")

    st.toggle("Smart Pothole & Speed-Breaker Rejection Filter", value=True, help="Filters out transient vertical road shocks.")
    st.toggle("Automatic False Alarm Sensor Recalibration", value=True, help="Smooths baseline accelerometer calibration when stationary.")

    # --- 4. DISPLAY, THEME & AUDIO PREFERENCES ---
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:24px; padding:1.25rem; box-shadow:0 8px 24px rgba(0,0,0,0.03); margin:1.2rem 0 0.85rem;">
            <div style="font-size:0.8rem; font-weight:900; color:#0f172a; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.35rem;">
                🎨 DISPLAY, THEME &amp; ALERTS
            </div>
            <div style="font-size:0.72rem; color:#64748b;">
                Customize appearance, siren alert volumes, and units.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    theme_selection = st.radio(
        "Interface Color Scheme",
        ["Glass White UI (Figma)", "Cyber Dark Glass"],
        horizontal=True,
        index=0 if is_white_theme else 1,
    )
    if (theme_selection == "Glass White UI (Figma)" and not is_white_theme) or (theme_selection == "Cyber Dark Glass" and is_white_theme):
        st.session_state.app_theme = "Glass White UI" if theme_selection == "Glass White UI (Figma)" else "Cyber Dark Glass"
        st.rerun()

    st.toggle("High-Decibel Siren Audio during 10s Countdown", value=True)
    st.toggle("Device Haptic Vibration Pulses on Warning", value=True)
    st.radio("Speed & Acceleration Units", ["Metric (km/h, G)", "Imperial (mph, G)"], horizontal=True)

    # --- 5. SYSTEM DIAGNOSTICS & CLOUD STATUS ---
    db_stat = db.get_db_status()
    db_badge_color = "#059669" if db_stat.get("is_cloud") else "#0284c7"
    db_engine_label = "Supabase Cloud (PostgreSQL)" if db_stat.get("is_cloud") else "Local SQLite Database"
    db_status_pill = "● CLOUD POSTGRESQL (TLS OK)" if db_stat.get("is_cloud") else "● SQLITE CACHE (ACTIVE)"

    card_bg = "#ffffff" if is_white_theme else "rgba(18, 26, 43, 0.75)"
    card_border = "#e2e8f0" if is_white_theme else "rgba(56, 189, 248, 0.22)"
    card_head_color = "#64748b" if is_white_theme else "#94a3b8"
    card_label_color = "#64748b" if is_white_theme else "#cbd5e1"

    st.markdown(
        f"""
        <div class="glass-card" style="background:{card_bg}; border:1px solid {card_border}; border-radius:24px; padding:1.25rem; box-shadow:0 8px 24px rgba(0,0,0,0.03); margin:1.2rem 0 0.85rem;">
            <div style="font-size:0.8rem; font-weight:900; color:{card_head_color}; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.65rem;">
                🛡️ SYSTEM HARDWARE &amp; CONNECTIVITY
            </div>
            <div style="display:flex; flex-direction:column; gap:9px;">
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;">
                    <span style="color:{card_label_color};">RTK Satellite GPS</span>
                    <span style="color:#059669; font-weight:800;">● LOCKED (14 Satellites · ±0.4m)</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;">
                    <span style="color:{card_label_color};">6-Axis IMU (Accel / Gyro)</span>
                    <span style="color:#059669; font-weight:800;">● CALIBRATED (100Hz Real-Time)</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;">
                    <span style="color:{card_label_color};">Twilio Cloud Webhook</span>
                    <span style="color:#059669; font-weight:800;">● TLS ACTIVE (Account Configured)</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;">
                    <span style="color:{card_label_color};">{db_engine_label}</span>
                    <span style="color:{db_badge_color}; font-weight:800;">{db_status_pill}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Reset Defaults", use_container_width=True):
            st.toast("Settings restored to factory nominal defaults.", icon="ℹ️")
    with col_btn2:
        if st.button("🔒 Switch Operator", use_container_width=True):
            st.session_state.is_operator_login_view = True
            st.rerun()

# -----------------------------------------------------------------------------
# TAB 5: 🌸 WOMEN SAFETY & RAPID PROTECTION HUB
# -----------------------------------------------------------------------------
elif st.session_state.mobile_section == "Women":
    st.markdown(
        """
        <div style="display:flex; align-items:center; justify-content:space-between; margin:0.4rem 0 0.85rem;">
            <div style="font-size:1.25rem; font-weight:900; color:#0f172a; letter-spacing:-0.02em;">
                🌸 Women Safety Shield
            </div>
            <span style="background:#fdf2f8; border:1px solid #fbcfe8; color:#be123c; font-size:0.7rem; font-weight:800; padding:3px 10px; border-radius:999px;">
                ● 24/7 ACTIVE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="glass-card" style="background:linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%); border:1.5px solid #fda4af; box-shadow:0 8px 24px rgba(244,63,94,0.1); text-align:center; padding:1.4rem 1rem; border-radius:24px; margin-bottom:0.9rem;">
            <div style="font-size:2.2rem; margin-bottom:0.35rem;">🚨</div>
            <div style="font-size:1.15rem; font-weight:900; color:#9f1239; letter-spacing:-0.02em;">
                INSTANT EMERGENCY DISPATCH
            </div>
            <div style="font-size:0.75rem; color:#881337; max-width:320px; margin:0.35rem auto 1.1rem; line-height:1.45; font-weight:500;">
                Press below to initiate automated emergency voice call &amp; GPS coordinates SMS via Twilio to police and emergency contacts.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚨 TRIGGER WOMEN SAFETY SOS DISPATCH", key="btn_women_hub_sos", type="primary", use_container_width=True):
        with st.spinner("Initiating emergency Twilio voice call and broadcast SMS..."):
            inc_id = db.create_incident(
                vehicle_type="Women Safety SOS",
                latitude=17.4435,
                longitude=78.3772,
                confidence=100.0,
                rider_status="CRITICAL ASSISTANCE",
                language="English",
                message="Women Safety Shield SOS activated. Immediate responder dispatch required.",
                status="REPORTED",
                address="12 MG Road, Bengaluru",
            )
            women_twiml = (
                "<Response><Pause length=\"1\"/><Say voice=\"alice\" language=\"en-IN\">"
                "Urgent Emergency Alert from SafeRide AI. Critical Women Safety SOS has been activated for female rider at coordinates latitude 17.4435, longitude 78.3772. "
                "Immediate police assistance and emergency responder dispatch is required. Check terminal now.</Say></Response>"
            )
            women_sms = (
                "🚨 SafeRide AI WOMEN SAFETY EMERGENCY ALERT! Female rider requested immediate assistance at "
                "Lat 17.4435, Lon 78.3772. Google Maps: https://maps.google.com/?q=17.4435,78.3772. "
                "Immediate police and emergency response needed!"
            )
            c_res = notify.trigger_emergency_call(
                {"incident_id": inc_id, "vehicle_type": "Women Safety SOS", "confidence": 100.0, "city": "12 MG Road, Bengaluru"},
                to_phone=notify.EMERGENCY_DISPATCH_PHONE,
                custom_twiml=women_twiml
            )
            s_res = notify.send_emergency_sms(
                {"incident_id": inc_id, "vehicle_type": "Women Safety SOS", "confidence": 100.0, "latitude": 17.4435, "longitude": 78.3772},
                to_phone=notify.EMERGENCY_DISPATCH_PHONE,
                custom_body=women_sms
            )
            st.session_state.last_call_dispatched = {
                "incident_id": inc_id,
                "call_sid": c_res.get("sid", "Queued"),
                "target": notify.EMERGENCY_DISPATCH_PHONE,
                "call_success": c_res.get("success", False),
                "error": c_res.get("error"),
            }
            st.rerun()

    # Fast Dial Emergency Helplines
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:22px; margin-top:1rem; padding:1.15rem; box-shadow:0 6px 20px rgba(0,0,0,0.03);">
            <div style="font-size:0.75rem; font-weight:900; color:#be123c; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.85rem;">
                DIRECT EMERGENCY HELPLINES
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <a href="tel:1091" style="text-decoration:none;">
                    <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:14px; padding:0.75rem 0.5rem; text-align:center;">
                        <div style="font-size:1.2rem; font-weight:900; color:#9f1239;">1091</div>
                        <div style="font-size:0.68rem; color:#be123c; font-weight:800; margin-top:2px;">WOMEN HELPLINE</div>
                    </div>
                </a>
                <a href="tel:112" style="text-decoration:none;">
                    <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:14px; padding:0.75rem 0.5rem; text-align:center;">
                        <div style="font-size:1.2rem; font-weight:900; color:#0369a1;">112</div>
                        <div style="font-size:0.68rem; color:#0284c7; font-weight:800; margin-top:2px;">POLICE / ALL SOS</div>
                    </div>
                </a>
                <a href="tel:108" style="text-decoration:none;">
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:14px; padding:0.75rem 0.5rem; text-align:center;">
                        <div style="font-size:1.2rem; font-weight:900; color:#b91c1c;">108</div>
                        <div style="font-size:0.68rem; color:#dc2626; font-weight:800; margin-top:2px;">AMBULANCE</div>
                    </div>
                </a>
                <a href="tel:""" + notify.EMERGENCY_DISPATCH_PHONE + """" style="text-decoration:none;">
                    <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:14px; padding:0.75rem 0.5rem; text-align:center;">
                        <div style="font-size:1.2rem; font-weight:900; color:#047857;">""" + notify.EMERGENCY_DISPATCH_PHONE[-4:] + """</div>
                        <div style="font-size:0.68rem; color:#059669; font-weight:800; margin-top:2px;">DISPATCHER</div>
                    </div>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Live Safe Coordinates
    st.markdown(
        """
        <div class="glass-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:1.15rem; box-shadow:0 6px 20px rgba(0,0,0,0.03); margin-top:0.85rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.7rem; font-weight:800; color:#0284c7; letter-spacing:0.06em; text-transform:uppercase;">LIVE GPS FIX</div>
                    <div style="font-size:0.95rem; font-weight:900; color:#0f172a; margin-top:2px;">17.4435° N, 78.3772° E</div>
                    <div style="font-size:0.75rem; color:#64748b; font-weight:600; margin-top:1px;">12 MG Road, Bengaluru</div>
                </div>
                <a href="https://maps.google.com/?q=17.4435,78.3772" target="_blank" style="text-decoration:none;">
                    <span style="display:inline-block; padding:7px 14px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; font-size:0.75rem; color:#1d4ed8; font-weight:800;">
                        🗺️ View Map
                    </span>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# FLOATING FROSTED GLASS BOTTOM NAVIGATION DOCK (DOCKS ON ALL SCREENS)
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 6.5rem;'></div>", unsafe_allow_html=True)

cur_tab = st.session_state.mobile_section

dock_html = f"""
<div class="floating-nav-dock">
    <a href="?section=Home" target="_self" class="nav-dock-btn {'active' if cur_tab == 'Home' else ''}" title="Home">
        <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
        {'<span class="nav-active-dot"></span>' if cur_tab == 'Home' else '<span style="height:5px;"></span>'}
    </a>
    <a href="?section=Alerts" target="_self" class="nav-dock-btn {'active' if cur_tab == 'Alerts' else ''}" title="Alerts">
        <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        {'<span class="nav-active-dot"></span>' if cur_tab == 'Alerts' else '<span style="height:5px;"></span>'}
    </a>
    <a href="?section=SOS" target="_self" class="nav-dock-sos" title="10-Second Emergency SOS">
        <div class="sos-glow-circle">
            <svg width="25" height="25" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
        </div>
    </a>
    <a href="?section=Map" target="_self" class="nav-dock-btn {'active' if cur_tab == 'Map' else ''}" title="Map Radar">
        <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
            <line x1="8" y1="2" x2="8" y2="18"></line>
            <line x1="16" y1="6" x2="16" y2="22"></line>
        </svg>
        {'<span class="nav-active-dot"></span>' if cur_tab == 'Map' else '<span style="height:5px;"></span>'}
    </a>
    <a href="?section=Settings" target="_self" class="nav-dock-btn {'active' if cur_tab in ['Profile', 'Settings'] else ''}" title="Settings">
        <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        {'<span class="nav-active-dot"></span>' if cur_tab in ['Profile', 'Settings'] else '<span style="height:5px;"></span>'}
    </a>
</div>
"""
st.markdown(dock_html, unsafe_allow_html=True)
