# PipeBot Media & Evidence Storage

This directory serves as the centralized repository for saved optical inspection evidence images, defect snapshots, and generated PDF compliance reports.

## Directory Layout

```text
media/
├── inspections/       # High-resolution JPEG/PNG frame captures of pipeline defects
└── reports/           # Generated PDF and structured JSON inspection mission reports
```

## Security & Path Traversal Protection

Media endpoints in the FastAPI backend enforce strict path sanitization:
- Only files within the authorized media root can be served.
- Dot-dot (`..`) path traversal attempts return HTTP 403 Forbidden.
- Permitted file extensions are restricted to: `.jpg`, `.jpeg`, `.png`, `.pdf`, `.json`.
