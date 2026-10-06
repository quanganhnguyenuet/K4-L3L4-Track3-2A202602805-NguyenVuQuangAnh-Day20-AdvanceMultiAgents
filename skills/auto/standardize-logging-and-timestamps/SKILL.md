---
name: standardize-logging-and-timestamps
description: Use this skill when parsing or generating logs to ensure consistent formatting, timestamp normalization, and service naming conventions.
---
- Extract timestamps and convert all to UTC timezone.
- Format timestamps as ISO 8601 UTC strings with 'Z' suffix (YYYY-MM-DDTHH:MM:SSZ).
- Normalize service names to lowercase and replace hyphens with underscores.
- Extract log levels and convert to uppercase.
- Parse multi-line log entries including tracebacks.
- Detect and sum repeated log message counts from “-- last message repeated N times --” lines.
- Sort log entries by service name and timestamp ascending.
- Include required metadata fields such as schema version and generator name.
- Validate output against schema and conventions before finalizing.
