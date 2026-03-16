# Monthly Sleep Graph `Beta`

> **Beta:** This endpoint is functional but still being refined. Response schema or data accuracy may change without notice.

Monthly sleep totals broken down by day and night — one data point per month with day/night split. This is the best endpoint for tracking long-term sleep trends, building month-over-month comparison charts, or analyzing seasonal sleep patterns.

## Request

```
GET /api/v1/sleep/monthly-sleep-graph
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
  "https://api.cradlewise.com/api/v1/sleep/monthly-sleep-graph?start_time=2025-01-01%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### Multi-Month Example

```json
{
  "age_banner_text": "8 weeks old",
  "plot_values": [
    {
      "day_sleep_in_mins": 90,
      "night_sleep_in_mins": 150,
      "total_sleep_in_mins": 240,
      "month": "2025-02-16 14:16:37.902395"
    },
    {
      "day_sleep_in_mins": 120,
      "night_sleep_in_mins": 234,
      "total_sleep_in_mins": 354,
      "month": "2025-03-18 14:16:37.902395"
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `age_banner_text` | string | Baby's age (e.g., `"8 weeks old"`) |
| `plot_values` | array | One entry per month in the requested range |

**Notable difference from weekly-sleep-graph:** There is no `timezone` field at the top level, and no `avg_*` summary fields. The response contains only the banner text and the monthly data points.

### Plot Value Object (per month)

| Field | Type | Description |
|-------|------|-------------|
| `day_sleep_in_mins` | number | Daytime sleep for this month, in minutes |
| `night_sleep_in_mins` | number | Nighttime sleep for this month, in minutes |
| `total_sleep_in_mins` | number | Total sleep for this month, in minutes (`day_sleep_in_mins + night_sleep_in_mins`) |
| `month` | string | Timestamp representing the month (`YYYY-MM-DD HH:MM:SS.ffffff`). Use the year and month portion only — the day/time component is not meaningful |

All sleep values are in **minutes** (not seconds). Day/night split is determined by the baby's configured day start time.

---

## Differences from Weekly Sleep Graph

| Aspect | `weekly-sleep-graph` | `monthly-sleep-graph` |
|--------|---------------------|-----------------------|
| Granularity | One entry per **day** | One entry per **month** |
| Date field | `date` | `month` |
| `timezone` field | Yes | **No** |
| `avg_*` fields | Yes (`avg_sleep_in_mins`, `avg_day_sleep_in_mins`, `avg_night_sleep_in_mins`) | **No** |
| Typical query span | 7 days | Several months to 14+ months |

---

## Practical Usage

### Querying the Last Year

Set `start_time` to 12 months ago and `end_time` to today:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-sleep-graph?start_time=2025-03-01%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Returns up to ~12 entries in `plot_values`, one per month.

### Month-over-Month Trend Analysis

```python
import requests
from datetime import datetime

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.cradlewise.com/api/v1"

resp = requests.get(f"{BASE}/sleep/monthly-sleep-graph", headers=HEADERS, params={
    "start_time": "2025-01-01 00:00:00",
    "end_time": "2026-03-13 00:00:00",
})
data = resp.json()

print(f"Baby info: {data['age_banner_text']}")
print(f"\nMonth-over-month sleep trends:")

prev_total = None
for entry in data["plot_values"]:
    month_str = datetime.strptime(entry["month"][:7], "%Y-%m").strftime("%B %Y")
    total_hrs = entry["total_sleep_in_mins"] / 60
    day_hrs = entry["day_sleep_in_mins"] / 60
    night_hrs = entry["night_sleep_in_mins"] / 60

    # Calculate change from previous month
    change = ""
    if prev_total is not None:
        delta = entry["total_sleep_in_mins"] - prev_total
        direction = "+" if delta >= 0 else ""
        change = f" ({direction}{delta:.0f} min)"

    print(f"  {month_str}: {total_hrs:.1f}h total (day: {day_hrs:.1f}h, night: {night_hrs:.1f}h){change}")
    prev_total = entry["total_sleep_in_mins"]
```

Example output:
```
Baby info: 8 weeks old

Month-over-month sleep trends:
  February 2025: 4.0h total (day: 1.5h, night: 2.5h)
  March 2025: 5.9h total (day: 2.0h, night: 3.9h) (+114 min)
```

### Extracting the Month from the Timestamp

The `month` field is a full timestamp, but only the month and year are meaningful. Parse accordingly:

```python
from datetime import datetime

for entry in data["plot_values"]:
    dt = datetime.strptime(entry["month"][:7], "%Y-%m")
    label = dt.strftime("%b %Y")  # "Feb 2025", "Mar 2025"
    print(f"{label}: {entry['total_sleep_in_mins']} min")
```

### Converting to Hours and Minutes

```python
def mins_to_hm(mins):
    h = int(mins // 60)
    m = int(mins % 60)
    return f"{h}h {m}m"

for entry in data["plot_values"]:
    month_label = entry["month"][:7]
    print(f"{month_label}: {mins_to_hm(entry['total_sleep_in_mins'])}")
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

### The `month` Field Is a Full Timestamp

The `month` field contains a full timestamp like `"2025-02-16 14:16:37.902395"`, not a clean month string. The day and time components are not meaningful — always parse only the year and month (`entry["month"][:7]`). Do not use the day or time portion for any logic.

### Large Historical Queries

A query spanning 14+ months returns ~14 entries in `plot_values` — one per month. The response is lightweight (a few KB) so large spans are fine from a performance standpoint. However, each request counts toward the shared daily rate limit.

### No Timezone Field

Unlike `weekly-sleep-graph`, this endpoint does not return a `timezone` field. If you need the baby's timezone, query `weekly-sleep-graph` or `c-chart` and use the timezone from that response.

### No Average Fields

Unlike `weekly-sleep-graph`, this endpoint does not return `avg_sleep_in_mins`, `avg_day_sleep_in_mins`, or `avg_night_sleep_in_mins`. Calculate averages yourself if needed:

```python
totals = [e["total_sleep_in_mins"] for e in data["plot_values"]]
avg_total = sum(totals) / len(totals) if totals else 0
```

### Future Dates

If the range extends into the future, those months may appear with zero values or may be omitted entirely from `plot_values`.

### Reversed Date Range (`start_time` > `end_time`)

Likely returns `200 OK` with empty `plot_values` or `500 Internal Server Error`. **Always validate that `start_time < end_time` in your code.**

### Empty Results

If no sleep data exists for the queried range (e.g., crib was not in use), `plot_values` may be an empty array `[]`.

### Day/Night Split

The boundary between "day sleep" and "night sleep" is determined by the baby's configured day start time setting, not by a fixed hour. This is the same boundary used across all sleep endpoints.

### Units Are Minutes

Like `weekly-sleep-graph`, this endpoint returns all sleep values in **minutes**. Do not divide by 3600 — divide by 60 to convert to hours.

---

## Error Responses

| Status | Cause | Response |
|--------|-------|----------|
| 401 | Missing or invalid token | `{"detail": "Missing authorization header"}` or `{"detail": "Invalid token"}` |
| 403 | No Nurture Plus subscription | `{"detail": "Nurture Plus subscription required"}` |
| 422 | Missing `start_time` or `end_time` | `{"detail": [{"msg": "Field required", ...}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded"}` |
| 500 | Invalid date format (e.g., T separator) | `Internal Server Error` |
