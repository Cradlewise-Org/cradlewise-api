# Monthly Rise and Bed Time

Monthly averages for rise time and bed time. One entry per month with the average wake-up and sleep-onset times for that period. Best for long-term trend analysis — shows how the baby's schedule shifts month over month.

## Request

```
GET /api/v1/sleep/monthly-rise-and-bed-time
```

### Parameters

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `start_time` | string | Yes | `YYYY-MM-DD HH:MM:SS` | Start of the time window (UTC) |
| `end_time` | string | Yes | `YYYY-MM-DD HH:MM:SS` | End of the time window (UTC) |

**Important:** Use space-separated format only. The `T` separator causes a `500` error.

### curl

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-rise-and-bed-time?start_time=2025-12-01%2000:00:00&end_time=2026-03-14%2000:00:00"
```

---

## Response

### Multi-Month Example

```json
{
  "plot_values": [
    {
      "rise_time": "2026-03-13 09:20:00.000000",
      "bed_time": "2026-03-13 21:00:00.000000",
      "month": "2026-03-13 00:00:00.000000"
    },
    {
      "rise_time": "2026-02-11 09:00:00.000000",
      "bed_time": "2026-02-11 21:30:00.000000",
      "month": "2026-02-11 00:00:00.000000"
    },
    {
      "rise_time": "2025-12-13 08:00:00.000000",
      "bed_time": "2025-12-13 18:30:00.000000",
      "month": "2025-12-13 00:00:00.000000"
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `plot_values` | array | One entry per month that has data within the requested range. Reverse chronological order (most recent first) |

**Note:** Unlike the weekly version, there is no `avg_rise_time`, `avg_bed_time`, or `day_start_time` at the top level. The response contains only `plot_values`.

### Plot Value Object (per month)

| Field | Type | Description |
|-------|------|-------------|
| `rise_time` | string | Average rise time for the month, expressed as a full UTC timestamp (`YYYY-MM-DD HH:MM:SS.ffffff`). The time portion is what matters — the date portion is incidental |
| `bed_time` | string | Average bed time for the month, expressed as a full UTC timestamp (`YYYY-MM-DD HH:MM:SS.ffffff`). The time portion is what matters — the date portion is incidental |
| `month` | string | A timestamp representing the month (`YYYY-MM-DD HH:MM:SS.ffffff`). Use the year and month portion for display |

---

## Practical Usage (Python)

### Tracking Schedule Consistency

```python
import requests
from datetime import datetime

headers = {"Authorization": "Bearer YOUR_TOKEN"}
params = {
    "start_time": "2025-12-01 00:00:00",
    "end_time": "2026-03-14 00:00:00"
}

resp = requests.get(
    "https://api.cradlewise.com/api/v1/sleep/monthly-rise-and-bed-time",
    headers=headers,
    params=params
)
data = resp.json()

for entry in data["plot_values"]:
    month_label = entry["month"][:7]  # "2026-03"
    rise = entry["rise_time"][11:19] if entry["rise_time"] else "—"
    bed = entry["bed_time"][11:19] if entry["bed_time"] else "—"
    print(f"{month_label}: Rise {rise}, Bed {bed}")
```

Example output:
```
2026-03: Rise 09:20:00, Bed 21:00:00
2026-02: Rise 09:00:00, Bed 21:30:00
2025-12: Rise 08:00:00, Bed 18:30:00
```

### Detecting Schedule Drift

```python
from datetime import datetime

def time_from_ts(ts):
    """Extract time-of-day from a full timestamp string."""
    return datetime.strptime(ts[11:19], "%H:%M:%S")

entries = data["plot_values"]

if len(entries) >= 2:
    latest = entries[0]
    previous = entries[1]

    rise_diff = time_from_ts(latest["rise_time"]) - time_from_ts(previous["rise_time"])
    bed_diff = time_from_ts(latest["bed_time"]) - time_from_ts(previous["bed_time"])

    rise_min = rise_diff.total_seconds() / 60
    bed_min = bed_diff.total_seconds() / 60

    print(f"Rise time shifted {rise_min:+.0f} min from last month")
    print(f"Bed time shifted {bed_min:+.0f} min from last month")
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Per hour | 60 requests |
| Daily cap (shared with all endpoints) | 500 requests |

### Rate Limit Response

```
HTTP/1.1 429 Too Many Requests
x-ratelimit-remaining: 0
x-ratelimit-reset: 1710288000
```

```json
{"detail": "Rate limit exceeded"}
```

---

## Edge Cases

### Reverse Chronological Order

Entries in `plot_values` are returned most-recent-first. If you need chronological order for charting, reverse the array:

```python
chronological = list(reversed(data["plot_values"]))
```

### Months With No Data

Months with no recorded sleep data are omitted entirely from `plot_values`. Unlike the weekly version (which returns empty-string entries for days without data), the monthly endpoint simply skips months. A query spanning December through March may return only 3 entries if January had no data.

### The Date Portion of Timestamps

The `rise_time`, `bed_time`, and `month` fields are full timestamps, but the date portion of `rise_time` and `bed_time` is incidental — it does not represent the specific day. Only the time portion (hours, minutes, seconds) carries meaning as the monthly average. Parse with:

```python
avg_rise_hour = entry["rise_time"][11:16]  # "09:20"
```

### Rise and Bed Timestamps Are UTC

The time values are in UTC. Convert to the baby's local timezone for display. This endpoint does not include a `timezone` field — use the timezone from the Day Metrics or Baby Status endpoint.

### No Top-Level Averages

Unlike the weekly version which returns `avg_rise_time` and `avg_bed_time` as human-readable strings, the monthly endpoint returns only `plot_values`. Compute your own cross-month averages if needed.

### Single-Month Query

If your range falls within a single month, `plot_values` will contain at most one entry.

### Empty Results

If no sleep data exists for the queried range, `plot_values` will be an empty array `[]`.

---

## Error Responses

| Status | Cause | Response |
|--------|-------|----------|
| 401 | Missing or invalid token | `{"detail": "Invalid token"}` |
| 403 | No Nurture Plus subscription | `{"detail": "Nurture Plus subscription required"}` |
| 422 | Missing required parameters | `{"detail": [{"msg": "Field required", ...}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded"}` |
| 500 | Invalid date format or `T` separator | `Internal Server Error` |
