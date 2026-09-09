# ⚡ Supabase & PostgreSQL Setup Guide for SafeRide AI

This guide walks you through connecting SafeRide AI to your **Supabase PostgreSQL Cloud Database** for real-time incident storage, telemetry streaming, and automated multi-client synchronization.

---

## 1. Create a Free Supabase Project

1. Navigate to **[supabase.com](https://supabase.com)** and sign in or create a free account.
2. Click **New Project**.
3. Choose your organization and specify:
   - **Name**: `saferide-ai`
   - **Database Password**: Choose a strong password and save it securely.
   - **Region**: Select the region closest to you (e.g. *South Asia (Mumbai)* or *Southeast Asia (Singapore)*).
4. Click **Create new project** and wait ~2 minutes for provisioning.

---

## 2. Execute the Database Schema (`supabase_schema.sql`)

1. In your Supabase Project dashboard, open the **SQL Editor** from the left navigation bar (icon: `>_`).
2. Click **New query**.
3. Open the file [`supabase_schema.sql`](../supabase_schema.sql) in this repository and copy its entire contents.
4. Paste the SQL into the Supabase query editor window.
5. Click **Run** (or press `Ctrl + Enter`).

You will see:
```sql
Success. No rows returned.
```
This automatically sets up:
- ✅ `public.incidents` table with full spatial and telemetry columns.
- ✅ `public.incident_messages` table for chat transcripts.
- ✅ `public.telemetry_logs` table for real-time sensor streams.
- ✅ High-performance indexes on timestamps and status flags.
- ✅ Row Level Security (RLS) policies allowing public read/write via the API.
- ✅ `supabase_realtime` publication for instant WebSocket push notifications.
- ✅ Initial verified incident records ready for demo use.

---

## 3. Retrieve API Credentials

1. In your Supabase Dashboard, click on **Project Settings** (gear icon at the bottom left).
2. Click on the **API** tab under Configuration.
3. Locate:
   - **Project URL**: Format `https://your-project-id.supabase.co`
   - **Project API Keys** -> `anon` / `public`: A long string starting with `eyJhbGci...`

---

## 4. Configure SafeRide AI Environment (`.env`)

Add your credentials to the `.env` file in the root of your project:

```ini
# --- Module 2: Cloud Database (Supabase & PostgreSQL) ---
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional Direct PostgreSQL Connection String (for ORM / direct pooling):
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres
```

---

## 5. Verify the Connection

Test the database connection from your terminal:

```bash
python -c "import database as db; print('Active Database Engine:', db.get_db_status()); print('Loaded Incidents:', len(db.get_all_incidents()))"
```

Expected output when configured:
```text
Active Database Engine: Supabase Cloud PostgreSQL (https://your-project-id.supabase.co)
Loaded Incidents: 4
```

> **Fallback Guarantee**: If `SUPABASE_URL` or `SUPABASE_KEY` are not set or there is no network connection, SafeRide AI automatically falls back to local SQLite (`saferide.db`) without throwing errors.

---

## 6. Real-Time Emergency Alerts

Because `supabase_realtime` is enabled in `supabase_schema.sql`, whenever a crash is detected by any mobile device or the simulator:
- The incident is instantly written to Supabase PostgreSQL.
- Any open operator dashboard or mobile companion can listen to database changes via WebSocket subscriptions.
