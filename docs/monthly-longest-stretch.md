# Monthly Longest Stretch

Monthly view of your baby's longest uninterrupted sleep stretch per month — useful for tracking sleep consolidation progress over time. Each month returns the single longest continuous sleep period along with three representations: raw minutes, decimal hours, and a human-readable display string.

## Request

```
GET /api/v1/sleep/monthly-longest-stretch
```

### Parameters

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `start_time` | string | Yes | `YYYY-MM-DD HH:MM:SS` | Start of the time window (UTC) |
| `end_time` | string | Yes | `YYYY-MM-DD HH:MM:SS` | End of the time window (UTC) |

**Important:** Use space-separated format (`2026-03-10 00:00:00`), not ISO 8601 with `T` separator. The `T` format causes a `500` error.

### curl

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-longest-stretch?start_time=2025-12-01%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### Multi-Month Example

```json
{
  "plot_values": [
    {
      "longest_stretch_in_mins": 300,
      "longest_stretch_in_hours": 5.0,
      "longest_stretch_display_text": "5h 0m",
      "month": "2026-03-13 03:46:40.842631"
    },
    {
      "longest_stretch_in_mins": 150,
      "longest_stretch_in_hours": 2.5,
      "longest_stretch_display_text": "2h 30m",
      "month": "2026-02-11 03:46:40.842631"
    },
    {
      "longest_stretch_in_mins": 370,
      "longest_stretch_in_hours": 6.2,
      "longest_stretch_display_text": "6h 10m",
      "month": "2025-12-13 03:46:40.842631"
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `plot_values` | array | One entry per month containing the longest uninterrupted sleep stretch for that month |

### Plot Value Object

| Field | Type | Description |
|-------|------|-------------|
| `longest_stretch_in_mins` | number | Longest uninterrupted sleep stretch for the month, in minutes |
| `longest_stretch_in_hours` | number | Same value in decimal hours (e.g., `2.5` = 2 hours 30 minutes) |
| `longest_stretch_display_text` | string | Human-readable format like `"5h 0m"` or `"6h 10m"` |
| `month` | string | Full timestamp representing the month (`YYYY-MM-DD HH:MM:SS.ffffff`). Use the year and month portion only — the day and time components are not meaningful |

---

## Date Format

**Use space-separated format only:**

| Format | Works? |
|--------|--------|
| `2026-03-10 00:00:00` | Yes |
| `2026-03-10%2000:00:00` | Yes (URL-encoded space) |
| `2026-03-10T00:00:00` | **No** — returns `500 Internal Server Error` |

This applies to all sleep endpoints, not just Monthly Longest Stretch.

---

## Practical Usage

### Querying the Last 6 Months

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-longest-stretch?start_time=2025-09-01%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Returns one entry per month where sleep data exists.

### Tracking Improvement Over Months (Python)

```python
import requests
from datetime import datetime

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.cradlewise.com/api/v1"

resp = requests.get(f"{BASE}/sleep/monthly-longest-stretch", headers=HEADERS, params={
    "start_time": "2025-09-01 00:00:00",
    "end_time": "2026-03-13 00:00:00",
})
data = resp.json()

# Sort by month (oldest first)
months = sorted(data["plot_values"], key=lambda m: m["month"])

print("Monthly Longest Sleep Stretch")
print("-" * 40)

for entry in months:
    month_label = datetime.strptime(entry["month"][:7], "%Y-%m").strftime("%B %Y")
    print(f"  {month_label}: {entry['longest_stretch_display_text']} ({entry['longest_stretch_in_hours']}h)")

# Check for improvement trend
if len(months) >= 2:
    first = months[0]["longest_stretch_in_mins"]
    last = months[-1]["longest_stretch_in_mins"]
    diff = last - first
    if diff > 0:
        print(f"\n  +{diff} minutes improvement from {months[0]['month'][:7]} to {months[-1]['month'][:7]}")
    elif diff < 0:
        print(f"\n  {diff} minutes decrease from {months[0]['month'][:7]} to {months[-1]['month'][:7]}")
    else:
        print(f"\n  No change between {months[0]['month'][:7]} and {months[-1]['month'][:7]}")
```

### Parsing the Month Field

The `month` field is a full timestamp, but only the year and month matter:

```python
from datetime import datetime

raw_month = "2026-03-13 03:46:40.842631"
parsed = datetime.strptime(raw_month[:7], "%Y-%m")
label = parsed.strftime("%B %Y")  # "March 2026"
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

### Months With No Sleep Data

Months where no sleep was recorded (crib off, baby not using the crib) are omitted from the `plot_values` array entirely. There is no entry with zero values — the month simply does not appear.

### Partial Months

A query starting mid-month still returns that month's longest stretch based on available data. The longest stretch reflects only sessions within the queried window, not the full calendar month.

### Single-Month Query

If `start_time` and `end_time` fall within the same month, `plot_values` contains at most one entry.

### Reversed Date Range (`start_time` > `end_time`)

Returns `200 OK` with an empty `plot_values` array. **No error is raised.** Always validate that `start_time < end_time` in your code.

### No Top-Level Average

Unlike the weekly longest stretch endpoint, this endpoint does **not** include an `avg_longest_stretch` field at the top level. If you need an average, compute it from the `plot_values` array:

```python
values = data["plot_values"]
if values:
    avg_mins = sum(v["longest_stretch_in_mins"] for v in values) / len(values)
    print(f"Average longest stretch: {avg_mins:.0f} minutes")
```

### Display Text Format

`longest_stretch_display_text` always uses the format `Xh Ym` (e.g., `"5h 0m"`, `"2h 30m"`). Minutes are always shown, even when zero.

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
BASE = "https://api.cradlewise.com/api/v1"

# Last 6 months
end = datetime.now()
start = end - timedelta(days=180)

fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")

resp = requests.get(f"{BASE}/sleep/monthly-longest-stretch", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

months = sorted(data["plot_values"], key=lambda m: m["month"])

print(f"Months with data: {len(months)}")

for entry in months:
    month_label = datetime.strptime(entry["month"][:7], "%Y-%m").strftime("%b %Y")
    mins = entry["longest_stretch_in_mins"]
    display = entry["longest_stretch_display_text"]
    print(f"\n  {month_label}: {display} ({mins} minutes)")
```
