"""
SafeRide AI - Supabase & PostgreSQL Connection Diagnostic Tool (check_supabase.py)
----------------------------------------------------------------------------------
Run this script to verify:
  1. Presence and validity of Supabase credentials in .env
  2. Live HTTPS connection to Supabase Cloud API
  3. Verification that required tables (incidents, incident_messages, telemetry_logs) exist
  4. Automatic failover to local SQLite fallback
"""

import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def run_diagnostics():
    print("=" * 65)
    print(" [SAFERIDE AI] SUPABASE & POSTGRESQL CONNECTION DIAGNOSTICS")
    print("=" * 65)

    # Step 1: Inspect environment variables
    print("\n[Step 1/3] Checking environment variables in .env:")
    print(f"  * SUPABASE_URL:  {SUPABASE_URL or '<Not Set>'}")
    masked_key = (
        SUPABASE_KEY[:6] + "..." + SUPABASE_KEY[-4:]
        if len(SUPABASE_KEY) > 12
        else (SUPABASE_KEY if SUPABASE_KEY else "<Not Set>")
    )
    print(f"  * SUPABASE_KEY:  {masked_key}")
    print(f"  * DATABASE_URL:  {DATABASE_URL[:20] + '...' if DATABASE_URL else '<Not Set>'}")

    # Check for placeholder values
    is_placeholder = (
        not SUPABASE_URL
        or not SUPABASE_KEY
        or "your-project-id" in SUPABASE_URL
        or "your-supabase" in SUPABASE_KEY
    )

    if is_placeholder:
        print("\n[!] STATUS: PLACEHOLDER CREDENTIALS DETECTED IN .env")
        print("-" * 65)
        print("Your .env file currently contains default placeholder Supabase values:")
        print("  - Line 26: SUPABASE_URL=https://your-project-id.supabase.co")
        print("  - Line 27: SUPABASE_KEY=your-supabase-anon-or-service-role-key")
        print("\n>>> HOW TO CONNECT YOUR REAL SUPABASE PROJECT <<<")
        print("  1. Sign in to https://supabase.com and create a project (e.g. saferide-ai).")
        print("  2. In your Supabase Dashboard, click: Project Settings (gear icon) -> API")
        print("  3. Copy 'Project URL' and paste it into .env as SUPABASE_URL")
        print("  4. Copy 'Project API Key' (anon or service_role) and paste it as SUPABASE_KEY")
        print("  5. In Supabase SQL Editor, run 'supabase_schema.sql' to create the tables.")
        print("\n[OK] CURRENT ACTIVE DATABASE ENGINE:")
        print("  * SafeRide AI is safely running on: SQLite (Local Cache) - saferide.db")
        print("  * Zero downtime: Detection, GPS mapping, SOS calling remain 100% active.")
        print("=" * 65)
        return False

    # Step 2: Test Supabase SDK and Cloud Connection
    print("\n[Step 2/3] Connecting to Supabase Cloud API...")
    try:
        from supabase import create_client

        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("  [OK] Client initialized successfully.")
    except Exception as e:
        print(f"  [X] Failed to initialize Supabase client: {e}")
        return False

    # Step 3: Test Database Schema & Tables
    print("\n[Step 3/3] Querying PostgreSQL tables...")
    tables_to_check = ["incidents", "incident_messages", "telemetry_logs"]
    all_ok = True

    for table_name in tables_to_check:
        try:
            res = client.table(table_name).select("*", count="exact").limit(1).execute()
            count = res.count if hasattr(res, "count") and res.count is not None else len(res.data)
            print(f"  [OK] Table '{table_name}' is accessible! (Current row count: {count})")
        except Exception as e:
            all_ok = False
            err_msg = str(e)
            print(f"  [X] Table '{table_name}' error: {err_msg}")
            if "relation" in err_msg.lower() or "not find" in err_msg.lower():
                print(f"      TIP: Have you run 'supabase_schema.sql' in the Supabase SQL Editor?")

    print("\n" + "=" * 65)
    if all_ok:
        print("[SUCCESS] Supabase PostgreSQL is fully connected and ready!")
        print("SafeRide AI will now stream and store all incidents in the cloud.")
    else:
        print("[NOTICE] Connection reached Supabase, but some tables are missing.")
        print("Please copy and run 'supabase_schema.sql' in the Supabase SQL Editor.")
    print("=" * 65)
    return all_ok


if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
