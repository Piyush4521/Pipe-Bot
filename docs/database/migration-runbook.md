# PipeBot Alembic Schema Migration Runbook

## 1. Revision History and Schema Evolution

The PipeBot database schema is managed through Alembic database migrations. Every schema alteration is version-controlled, reversible, and tested against isolated temporary databases prior to release.

```
       +-------------------------------------------------------------+
       |                         (base)                              |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       | Revision: 88f24fc2264d                                      |
       | Stage 1: Initial Inspections and Defects Tables             |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       | Revision: d4d255efae0c  (ACTIVE DATABASE HEAD)               |
       | Stage 2: Audit-Safe Retention & Strict Foreign Keys         |
       | - Prohibits destructive cascades                            |
       | - Adds soft deletion and UTC timestamp normalization        |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       | Revision: e7f8a9b0c1d2  (STAGE 3 IMPLEMENTED HEAD)          |
       | Stage 3: Telemetry, Hardware Devices, AI Provenance,        |
       | Media Evidence, Analytics, Reports, and Security Audit      |
       +-------------------------------------------------------------+
```

---

## 2. Active Database Status

As verified by the non-destructive inspection audit on 2026-10-30:
- Active Database Location: `D:\PipeBot\backend\data\pipebot.db`
- Current Alembic Revision: `['d4d255efae0c']`
- Migration Status: The live database currently resides at Stage 2 head. The new Stage 3 migration (`e7f8a9b0c1d2`) has been fully validated in automated test suites and isolated databases, but has not yet been applied to the active database file per strict release boundary guidelines.

---

## 3. Forward Migration Runbook (Applying e7f8a9b0c1d2)

When authorized to upgrade the live database from `d4d255efae0c` to `e7f8a9b0c1d2`, execute the following sequential workflow:

### Step 1: Pre-Migration Backup
Always capture an online backup before running DDL modifications:
```bash
cd /mnt/d/PipeBot/backend
PYTHONPATH=. .venv/bin/python -c "
from app.db.backup import backup_sqlite_database
result = backup_sqlite_database('data/pipebot.db', 'backups/database')
print('Pre-migration backup created:', result['backup_path'])
"
```

### Step 2: Dry-Run SQL Generation
Inspect the generated SQL DDL statements without executing them:
```bash
.venv/bin/alembic upgrade d4d255efae0c:e7f8a9b0c1d2 --sql > migration_dryrun.sql
cat migration_dryrun.sql
```
Verify that all statements use non-destructive table additions (`CREATE TABLE`, `CREATE INDEX`).

### Step 3: Execute Migration
Apply the migration to the active database:
```bash
.venv/bin/alembic upgrade head
```

### Step 4: Post-Migration Validation
Validate that all 16 domain tables exist and integrity is intact:
```bash
PYTHONPATH=. .venv/bin/python scripts/inspect_active_db.py
```
Check that:
- Current revision is reported as `['e7f8a9b0c1d2']`.
- `PRAGMA integrity_check` reports `ok`.
- `PRAGMA foreign_key_check` reports 0 violations.
- Historical inspection and defect records remain untouched.

---

## 4. Rollback and Downgrade Runbook

### 4.1 Safe Partial Downgrade (e7f8a9b0c1d2 -> d4d255efae0c)
If operational issues arise with the new telemetry tables, the schema can be downgraded to the prior baseline without losing core inspection or defect records:

```bash
cd /mnt/d/PipeBot/backend
.venv/bin/alembic downgrade d4d255efae0c
```

What occurs during downgrade:
- Stage 3 tables (`devices`, `encoder_samples`, `imu_samples`, `camera_frames`, `evidence_media`, `ai_model_versions`, `localization_records`, `inspection_events`, `inspection_summaries`, `inspection_reports`, `audit_events`) are cleanly dropped.
- `inspections` and `defects` tables are preserved.
- Alembic revision table updates to `['d4d255efae0c']`.

### 4.2 Handling Foreign Key Lockouts During Downgrade
In SQLite, executing batch alter table commands on parent tables while child tables contain active rows will cause `FOREIGN KEY constraint failed`.
Safeguard:
- Always ensure child defect records referencing inspections are either resolved or archived prior to dropping or restructuring parent tables.

---

## 5. Emergency Rollback Playbook

If a migration fails mid-execution or leaves the database in an inconsistent state:

Step 1: Terminate all backend workers:
```bash
pkill -f "uvicorn app.main:app"
```

Step 2: Restore from the pre-migration backup captured in Step 1:
```bash
PYTHONPATH=. .venv/bin/python -c "
from app.db.backup import restore_sqlite_database
res = restore_sqlite_database('backups/database/<pre_migration_backup_name>.db', 'data/pipebot.db')
print('Database restored to pre-migration baseline:', res['status'])
"
```

Step 3: Verify the restored database:
```bash
PYTHONPATH=. .venv/bin/python scripts/inspect_active_db.py
```

Step 4: Check application health:
```bash
.venv/bin/pytest tests/test_health.py -v
```

