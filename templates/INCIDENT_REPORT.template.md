---
artifact_id: "ART-YYYYMMDD-IR-NNN"
artifact_type: "INCIDENT_REPORT"
title: "Incident Report: [Brief Description]"
version: "1.0.0"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
owner_agent: "data_observability_agent"
severity: "P0 | P1 | P2 | P3"
status: "OPEN | INVESTIGATING | RESOLVED | POSTMORTEM_COMPLETE"
---

# Incident Report: [Brief Description]

## 1. Incident Summary

| Field | Value |
|---|---|
| **Incident ID** | INC-YYYYMMDD-NNN |
| **Severity** | P0 / P1 / P2 / P3 |
| **Status** | OPEN / INVESTIGATING / RESOLVED |
| **Detected At** | YYYY-MM-DD HH:MM UTC |
| **Resolved At** | YYYY-MM-DD HH:MM UTC |
| **Duration** | X hours Y minutes |
| **Impact** | [Description of business impact] |
| **Affected Systems** | [Pipeline / Model / Dashboard / API] |

---

## 2. Timeline

| Time (UTC) | Event |
|---|---|
| HH:MM | Anomaly first detected by [monitoring system] |
| HH:MM | Alert triggered — [channel] |
| HH:MM | Investigation started by [agent/person] |
| HH:MM | Root cause identified |
| HH:MM | Fix applied |
| HH:MM | Verification passed |
| HH:MM | Incident resolved |

---

## 3. Root Cause Analysis

### What happened?
[Detailed description of what went wrong]

### Why did it happen?
[5-Whys analysis or causal chain]

1. **Why?** →
2. **Why?** →
3. **Why?** →
4. **Why?** →
5. **Why?** → [Root cause]

### Evidence
- `[OBSERVATION]` [What was observed in logs/data]
- `[MEASURED_RESULT]` [Quantified impact]

---

## 4. Impact Assessment

| Metric | Before Incident | During Incident | After Fix |
|---|---|---|---|
| [Affected metric] | | | |
| Data freshness | | | |
| Pipeline success rate | | | |

### Data Impact
- Rows affected: [number]
- Time window of bad data: [start] to [end]
- Downstream consumers notified: ☐ Yes / ☐ No

---

## 5. Resolution

### Fix Applied
[Description of the fix]

### Verification
- [x] Fix tested in isolation
- [x] Rerun on affected data
- [x] Quality gates re-evaluated
- [x] Downstream data refreshed

---

## 6. Action Items (Preventing Recurrence)

| # | Action | Owner | Due Date | Status |
|---|---|---|---|---|
| 1 | [Preventive action] | | | ☐ TODO |
| 2 | [Monitoring improvement] | | | ☐ TODO |
| 3 | [Process change] | | | ☐ TODO |

---

## 7. Lessons Learned

### What went well
- [Positive aspects of incident response]

### What could be improved
- [Areas for improvement]

### Playbook Updates
- [x] Runbook updated: [link]
- [x] Alert rules updated: [link]
- [x] Monitoring dashboard updated: [link]
