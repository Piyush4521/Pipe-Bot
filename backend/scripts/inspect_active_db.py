"""Inspect the active SQLite database without modifying it."""

import datetime
from pathlib import Path
import sqlite3
import sys

backend_dir = Path(__file__).resolve().parent.parent
env_file = backend_dir / ".env"
env_url = None
if env_file.exists():
    for line in open(env_file, "r", encoding="utf-8"):
        if line.strip().startswith("DATABASE_URL"):
            env_url = line.strip().split("=", 1)[1].strip()

# Check settings resolution from code
sys.path.insert(0, str(backend_dir))
try:
    from app.core.config import get_settings
    settings = get_settings()
    settings_db_url = settings.database_url
    resolved_db_url = settings.resolved_database_url
except Exception as e:
    settings_db_url = f"Error: {e}"
    resolved_db_url = f"Error: {e}"

db_path = backend_dir / "data" / "pipebot.db"
exists = db_path.exists()
stat = db_path.stat() if exists else None
size_bytes = stat.st_size if stat else 0
mtime = datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc).isoformat() if stat else None

print("=== ACTIVE DATABASE INSPECTION ===")
print(f"ENV_FILE_DATABASE_URL: {env_url}")
print(f"SETTINGS_DATABASE_URL: {settings_db_url}")
print(f"RESOLVED_DATABASE_URL: {resolved_db_url}")
print(f"DATABASE_PATH: {db_path}")
print(f"EXISTS: {exists}")
print(f"SIZE_BYTES: {size_bytes}")
print(f"MODIFIED_UTC: {mtime}")

if exists:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()

    cur.execute("SELECT version_num FROM alembic_version")
    alembic_v = [r[0] for r in cur.fetchall()]
    print(f"ALEMBIC_REVISION: {alembic_v}")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"TABLES_FOUND: {tables}")

    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [f"{col[1]} ({col[2]}, notnull={col[3]}, pk={col[5]})" for col in cur.fetchall()]
        cur.execute(f"SELECT count(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f"TABLE {t} (row_count={cnt}):")
        for c in cols:
            print(f"  - {c}")

    for t in ["inspections", "defects"]:
        if t in tables:
            cur.execute(f"SELECT * FROM {t}")
            rows = cur.fetchall()
            print(f"ROWS_IN_{t} ({len(rows)}):")
            for r in rows:
                print(f"  {r}")

    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchall()
    print(f"PRAGMA integrity_check: {integrity}")

    cur.execute("PRAGMA foreign_key_check")
    fk_check = cur.fetchall()
    print(f"PRAGMA foreign_key_check: {fk_check}")

    conn.close()

