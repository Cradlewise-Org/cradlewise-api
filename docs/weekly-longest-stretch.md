# Weekly Longest Stretch `Beta`

> **Beta:** This endpoint is functional but still being refined. Response schema or data accuracy may change without notice.

The longest uninterrupted sleep stretch per day, with averages across the queried period. Use this to track whether your baby's longest continuous sleep block is trending longer over time — the key metric most parents care about for "sleeping through the night."

## Request

```
GET /api/v1/sleep/weekly-longest-stretch
```

### Parameters

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `start_time` | string | Yes | `YYYY-MM-DD HH:MM:SS` | Start of the time window (UTC) |
| `end_time` | string | Yes | `YYYY-MM-DD HH:MM:SS` | End of the time window (UTC) |

**Important:** Use space-separated format (`2026-03-06 00:00:00`), not ISO 8601 with `T` separator. The `T` format causes a `500` error.

### curl

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/weekly-longest-stretch?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### 7-Day Example

```json
{
  "avg_longest_stretch_in_mins": 4827.25,
  "avg_longest_stretch_display_text": "80h 27m",
  "plot_values": [
    {
      "longest_stretch_in_mins": 9766.0,
      "longest_stretch_in_hours": 162.8,
      "longest_stretch_display_text": "162h 46m",
      "date": "2026-03-06 02:30:00.000000"
    },
    {
      "longest_stretch_in_mins": 2491.0,
      "longest_stretch_in_hours": 41.5,
      "longest_stretch_display_text": "41h 31m",
      "date": "2026-03-07 02:30:00.000000"
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `avg_longest_stretch_in_mins` | number | Average of all daily longest stretches across the queried period, in minutes |
| `avg_longest_stretch_display_text` | string | Human-readable average (e.g., `"80h 27m"`) |
| `plot_values` | array | One entry per day that has sleep data |

### Plot Value Object

| Field | Type | Description |
|-------|------|-------------|
| `longest_stretch_in_mins` | number | Longest uninterrupted sleep stretch for that day, in minutes |
| `longest_stretch_in_hours` | number | Same value in decimal hours (e.g., `41.5` = 41h 30m) |
| `longest_stretch_display_text` | string | Human-readable duration (e.g., `"41h 31m"`) |
| `date` | string | Day boundary timestamp (`YYYY-MM-DD HH:MM:SS.ffffff`). Uses the baby's `day_start_time` offset, not midnight |

---

## Date Format

**Use space-separated format only:**

| Format | Works? |
|--------|--------|
| `2026-03-06 00:00:00` | Yes |
| `2026-03-06%2000:00:00` | Yes (URL-encoded space) |
| `2026-03-06T00:00:00` | **No** — returns `500 Internal Server Error` |

This applies to all sleep endpoints, not just Weekly Longest Stretch.

---

## Practical Usage

### Querying a Week

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/weekly-longest-stretch?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Returns up to 7 entries in `plot_values` (one per day with recorded sleep data).

### Tracking Longest Stretch Trends (Python)

```python
import requests
from datetime import datetime, timedelta

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://integrations.cradlewise.com/api/v1"

# Last 7 days
end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")

resp = requests.get(f"{BASE}/sleep/weekly-longest-stretch", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

print(f"Average longest stretch: {data['avg_longest_stretch_display_text']}")
print(f"Average longest stretch (mins): {data['avg_longest_stretch_in_mins']}")

for day in data["plot_values"]:
    date_str = day["date"][:10]
    mins = day["longest_stretch_in_mins"]
    hours = mins / 60
    print(f"  {date_str}: {day['longest_stretch_display_text']} ({hours:.1f}h)")

# Check if longest stretch is improving week-over-week
values = [d["longest_stretch_in_mins"] for d in data["plot_values"]]
if len(values) >= 2:
    first_half = sum(values[:len(values)//2]) / (len(values)//2)
    second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
    trend = "improving" if second_half > first_half else "declining"
    print(f"\nTrend: {trend} (first half avg: {first_half:.0f}m, second half avg: {second_half:.0f}m)")
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

### Days with No Sleep Data

Days where the crib recorded no sleep activity are **omitted** from `plot_values`. A 7-day query may return fewer than 7 entries. The average (`avg_longest_stretch_in_mins`) is computed only over days that have data.

### Very Large Values

Values like `162h 46m` (9,766 minutes) can appear when the baby stays asleep across multiple days or when test/debug data is present. In production with real usage, typical longest stretches for infants range from 2-12 hours. Consider clamping or flagging values above 24 hours as anomalous.

### `date` Uses `day_start_time` Offset

The `date` field (e.g., `2026-03-06 02:30:00.000000`) reflects the baby's configured day boundary, not midnight. This offset matches the baby's `day_start_time` setting. A date of `2026-03-06 02:30:00` means "the day starting at 2:30 AM on March 6th."

### Reversed Date Range (`start_time` > `end_time`)

Returns `200 OK` with empty `plot_values` and zero/null averages. **No error is raised.** Always validate that `start_time < end_time` in your code.

### Empty Results

If no sleep data exists for the queried window:
- `plot_values`: empty array `[]`
- `avg_longest_stretch_in_mins`: `0` or `null`
- `avg_longest_stretch_display_text`: `"0h 0m"` or empty string

This happens with future dates, very old dates, or periods when the crib was off.

### Invalid Date Strings

Non-date strings (e.g., `start_time=invalid`) return `500 Internal Server Error`. Always validate inputs before sending.

---

## Error Responses

| Status | Cause | Response |
|--------|-------|----------|
| 401 | Missing or invalid token | `{"detail": "Missing authorization header"}` or `{"detail": "Invalid token"}` |
| 403 | No Nurture Plus subscription | `{"detail": "Nurture Plus subscription required"}` |
| 422 | Missing `start_time` or `end_time` | `{"detail": [{"msg": "Field required", ...}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded"}` |
| 500 | Invalid date format (e.g., T separator) | `Internal Server Error` |

---

## Full Example (Python)

```python
import requests
from datetime import datetime, timedelta

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://integrations.cradlewise.com/api/v1"

# Last 7 days
end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")

resp = requests.get(f"{BASE}/sleep/weekly-longest-stretch", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

print(f"Average longest stretch: {data['avg_longest_stretch_display_text']}")

for day in data["plot_values"]:
    date_str = day["date"][:10]
    print(f"\n  {date_str}:")
    print(f"    Longest stretch: {day['longest_stretch_display_text']}")
    print(f"    In minutes: {day['longest_stretch_in_mins']}")
    print(f"    In hours: {day['longest_stretch_in_hours']}")
```
