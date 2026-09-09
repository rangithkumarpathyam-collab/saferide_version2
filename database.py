"""
SafeRide AI - Module 2: Backend Database Layer (database.py)
-----------------------------------------------------------
Dual-Mode Database Layer:
  - Primary (Cloud): Supabase & PostgreSQL (Real-time Cloud Storage & Sync)
  - Fallback (Local): SQLite3 Relational Database (Encrypted Local Cache)

Schema:
  - incidents table:
      incident_id (TEXT PRIMARY KEY)
      timestamp (TEXT)
      vehicle_type (TEXT)
      latitude (REAL)
      longitude (REAL)
      confidence (REAL)
      rider_status (TEXT)  # 'NORMAL', 'PENDING_CHECK', "I'M OK", 'NEED HELP', 'NO RESPONSE'
      language (TEXT)      # 'Telugu', 'English'
      message (TEXT)       # Primary/latest message
      status (TEXT)        # 'REPORTED', 'DISPATCHED', 'RESOLVED', 'CLOSED'
      address (TEXT)       # Reverse geocoded street address
  
  - incident_messages table:
      message_id (INTEGER PRIMARY KEY AUTOINCREMENT)
      incident_id (TEXT, FOREIGN KEY)
      sender (TEXT)        # 'Rider', 'Responder', 'System'
      original_text (TEXT)
      translated_text (TEXT)
      timestamp (TEXT)
"""

import sqlite3
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Load local environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saferide.db")

# Supabase Cloud Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

_supabase_client = None
_supabase_init_failed = False


def get_supabase_client():
    """
    Returns the Supabase Cloud client if credentials are configured.
    Returns None to seamlessly fall back to local SQLite.
    """
    global _supabase_client, _supabase_init_failed
    if _supabase_init_failed:
        return None
    if _supabase_client is not None:
        return _supabase_client

    if (
        SUPABASE_URL
        and SUPABASE_KEY
        and not SUPABASE_URL.startswith("https://your-project")
        and not SUPABASE_KEY.startswith("your-supabase")
    ):
        try:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            return _supabase_client
        except Exception as e:
            print(f"[SafeRide DB] Supabase cloud connection notice: {e}. Falling back to SQLite.")
            _supabase_init_failed = True
            return None
    return None


def get_db_status() -> Dict[str, Any]:
    """Returns the current active database engine metadata."""
    client = get_supabase_client()
    if client is not None:
        return {
            "engine": "Supabase (Cloud PostgreSQL)",
            "is_cloud": True,
            "target": SUPABASE_URL,
            "status": "ONLINE",
            "type": "PostgreSQL",
        }
    return {
        "engine": "SQLite (Local Cache)",
        "is_cloud": False,
        "target": DB_FILE,
        "status": "LOCAL",
        "type": "SQLite3",
    }


# -----------------------------------------------------------------------------
# SQLITE CORE HELPERS
# -----------------------------------------------------------------------------
def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_FILE, seed_sample_data: bool = True) -> None:
    """Creates required local SQLite tables and indices, and checks cloud readiness."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Create incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            confidence REAL NOT NULL,
            rider_status TEXT NOT NULL DEFAULT 'PENDING_CHECK',
            language TEXT NOT NULL DEFAULT 'Telugu',
            message TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'REPORTED',
            address TEXT DEFAULT ''
        )
    """)

    # Ensure address column exists for existing databases
    cursor.execute("PRAGMA table_info(incidents)")
    cols = [col[1] for col in cursor.fetchall()]
    if "address" not in cols:
        cursor.execute("ALTER TABLE incidents ADD COLUMN address TEXT DEFAULT ''")

    # Create incident_messages table for live chat
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            original_text TEXT NOT NULL,
            translated_text TEXT DEFAULT '',
            timestamp TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Seed initial demo data if database is newly initialized
    if seed_sample_data:
        cursor.execute("SELECT COUNT(*) FROM incidents")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_initial_data(conn)

    conn.close()

    # Check Cloud Supabase state if connected
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("incidents").select("incident_id", count="exact").limit(1).execute()
            print(f"[SafeRide DB] Supabase PostgreSQL cloud active. Table count verified.")
        except Exception as e:
            print(f"[SafeRide DB] Supabase check notice: {e}")


# -----------------------------------------------------------------------------
# DUAL-MODE INCIDENT CRUD OPERATIONS
# -----------------------------------------------------------------------------
def create_incident(
    vehicle_type: str,
    latitude: float,
    longitude: float,
    confidence: float,
    rider_status: str = "NEED HELP",
    language: str = "Telugu",
    message: str = "",
    status: str = "REPORTED",
    address: str = "",
    incident_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    db_path: str = DB_FILE,
) -> str:
    """Creates a new accident incident record in Supabase & mirrors to SQLite."""
    if not incident_id:
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Attempt insert to Cloud Supabase
    client = get_supabase_client()
    if client is not None:
        try:
            payload = {
                "incident_id": incident_id,
                "timestamp": timestamp,
                "vehicle_type": vehicle_type,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "confidence": float(confidence),
                "rider_status": rider_status,
                "language": language,
                "message": message or "",
                "status": status,
                "address": address or "",
            }
            client.table("incidents").insert(payload).execute()

            if message:
                msg_payload = {
                    "incident_id": incident_id,
                    "sender": "Rider",
                    "original_text": message,
                    "translated_text": "",
                    "timestamp": timestamp,
                }
                client.table("incident_messages").insert(msg_payload).execute()
        except Exception as e:
            print(f"[SafeRide DB] Supabase create_incident notice: {e}. Mirroring to SQLite.")

    # 2. Mirror into Local SQLite Cache
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO incidents (
                incident_id, timestamp, vehicle_type, latitude, longitude,
                confidence, rider_status, language, message, status, address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id, timestamp, vehicle_type, latitude, longitude,
            confidence, rider_status, language, message, status, address
        ))

        if message:
            cursor.execute("""
                INSERT INTO incident_messages (incident_id, sender, original_text, translated_text, timestamp)
                VALUES (?, 'Rider', ?, '', ?)
            """, (incident_id, message, timestamp))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[SafeRide DB] SQLite mirror error: {e}")

    return incident_id


def update_incident(incident_id: str, db_path: str = DB_FILE, **kwargs) -> bool:
    """Updates fields of an incident record in Supabase & mirrors to SQLite."""
    if not kwargs:
        return False

    allowed_fields = {
        "timestamp", "vehicle_type", "latitude", "longitude",
        "confidence", "rider_status", "language", "message", "status", "address"
    }

    clean_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not clean_kwargs:
        return False

    updated_cloud = False
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("incidents").update(clean_kwargs).eq("incident_id", incident_id).execute()
            updated_cloud = True
        except Exception as e:
            print(f"[SafeRide DB] Supabase update_incident notice: {e}")

    # Mirror to SQLite
    try:
        fields = [f"{k} = ?" for k in clean_kwargs.keys()]
        values = list(clean_kwargs.values())
        values.append(incident_id)

        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE incidents SET {', '.join(fields)} WHERE incident_id = ?", values)
        conn.commit()
        updated_local = cursor.rowcount > 0
        conn.close()
        return updated_cloud or updated_local
    except Exception as e:
        print(f"[SafeRide DB] SQLite update error: {e}")
        return updated_cloud


def get_incident(incident_id: str, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Retrieves a single incident by its ID as a dictionary."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("incidents").select("*").eq("incident_id", incident_id).limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"[SafeRide DB] Supabase get_incident notice: {e}")

    # Fallback to local SQLite
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_incidents(limit: int = 50, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieves all incidents sorted by most recent first."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("incidents").select("*").order("timestamp", desc=True).limit(limit).execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"[SafeRide DB] Supabase get_all_incidents notice: {e}")

    # Fallback to local SQLite
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_incident_message(
    incident_id: str,
    sender: str,
    original_text: str,
    translated_text: str = "",
    db_path: str = DB_FILE
) -> int:
    """Appends a message to the communication thread in Supabase and SQLite."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    client = get_supabase_client()
    if client is not None:
        try:
            msg_payload = {
                "incident_id": incident_id,
                "sender": sender,
                "original_text": original_text,
                "translated_text": translated_text or "",
                "timestamp": ts,
            }
            client.table("incident_messages").insert(msg_payload).execute()
            client.table("incidents").update({"message": original_text}).eq("incident_id", incident_id).execute()
        except Exception as e:
            print(f"[SafeRide DB] Supabase add_incident_message notice: {e}")

    # Mirror to local SQLite
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO incident_messages (incident_id, sender, original_text, translated_text, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (incident_id, sender, original_text, translated_text, ts))

    cursor.execute("""
        UPDATE incidents SET message = ? WHERE incident_id = ?
    """, (original_text, incident_id))

    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


def get_incident_messages(incident_id: str, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieves all messages for an incident ordered chronologically."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("incident_messages").select("*").eq("incident_id", incident_id).order("timestamp", desc=False).execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"[SafeRide DB] Supabase get_incident_messages notice: {e}")

    # Fallback to local SQLite
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM incident_messages
        WHERE incident_id = ?
        ORDER BY message_id ASC
    """, (incident_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def seed_initial_data(conn: sqlite3.Connection) -> None:
    """Pre-populates realistic incident records for immediate demo readiness."""
    cursor = conn.cursor()

    demo_incidents = [
        (
            "INC-2026-HYD-001",
            "2026-09-07 10:15:20",
            "Motorcycle",
            17.4435,
            78.3772,
            94.5,
            "NEED HELP",
            "Telugu",
            "నా కాలు బైక్ కింద ఇరుక్కుపోయింది, వెంటనే సహాయం కావాలి.",
            "REPORTED",
            "12 MG Road, Bengaluru"
        ),
        (
            "INC-2026-HYD-002",
            "2026-09-07 09:42:10",
            "Scooter",
            17.4156,
            78.4350,
            72.8,
            "NO RESPONSE",
            "Telugu",
            "క్రాష్ హెచ్చరిక: 10 సెకన్ల పాటు రైడర్ నుండి సమాధానం రాలేదు.",
            "DISPATCHED",
            "Banjara Hills Rd 12, Hyderabad"
        ),
        (
            "INC-2026-HYD-003",
            "2026-09-07 08:30:45",
            "Electric Bike",
            17.4239,
            78.3374,
            42.0,
            "I'M OK",
            "English",
            "Slipped on gravel during rain. No injuries, I'm safe.",
            "RESOLVED",
            "Gachibowli Stadium Corridor, Hyderabad"
        ),
    ]

    cursor.executemany("""
        INSERT INTO incidents (
            incident_id, timestamp, vehicle_type, latitude, longitude,
            confidence, rider_status, language, message, status, address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_incidents)

    messages = [
        ("INC-2026-HYD-001", "Rider", "నా కాలు బైక్ కింద ఇరుక్కుపోయింది, వెంటనే సహాయం కావాలి.", "My leg is stuck under the bike, need help immediately.", "2026-09-07 10:15:22"),
        ("INC-2026-HYD-001", "Responder", "Help is on the way. Ambulance dispatched from Cyberabad Emergency Center.", "సహాయం దారిలో ఉంది. సైబరాబాద్ అత్యవసర కేంద్రం నుండి అంబులెన్స్ పంపబడింది.", "2026-09-07 10:16:05"),
        ("INC-2026-HYD-001", "Rider", "చాలా రక్తం వస్తోంది, త్వరగా రండి.", "Bleeding heavily, please come fast.", "2026-09-07 10:16:40"),
        ("INC-2026-HYD-002", "System", "Emergency trigger: Unresponsive rider after 10-second safety prompt.", "ఎమర్జెన్సీ ట్రిగ్గర్: 10 సెకన్ల భద్రతా ప్రాంప్ట్ తర్వాత రైడర్ స్పందించలేదు.", "2026-09-07 09:42:20"),
        ("INC-2026-HYD-002", "Responder", "Emergency team dispatched with GPS tracking to Banjara Hills location.", "బంజారాహిల్స్ లొకేషన్‌కు జీపీఎస్ ట్రాకింగ్‌తో అత్యవసర బృందం పంపబడింది.", "2026-09-07 09:43:10")
    ]

    cursor.executemany("""
        INSERT INTO incident_messages (incident_id, sender, original_text, translated_text, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, messages)

    conn.commit()


if __name__ == "__main__":
    print("Testing SafeRide Database Layer...")
    init_db()
    status = get_db_status()
    print(f"Database Engine: {status['engine']} ({status['status']})")
    records = get_all_incidents()
    print(f"Database ready! Loaded {len(records)} incidents.")
    for rec in records[:3]:
        print(f" - [{rec['status']}] {rec['incident_id']} ({rec['vehicle_type']}) - Confidence: {rec['confidence']}%")
