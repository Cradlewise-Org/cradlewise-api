# Weekly Sleep Graph `Beta`

> **Beta:** This endpoint is functional but still being refined. Response schema or data accuracy may change without notice.

Weekly sleep totals broken down by day and night — average sleep durations across the period, plus daily breakdowns. This is the best endpoint for building a weekly sleep bar chart or tracking sleep trends over time.

## Request

```
GET /api/v1/sleep/weekly-sleep-graph
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
  "https://api.cradlewise.com/api/v1/sleep/weekly-sleep-graph?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### 7-Day Example

```json
{
  "timezone": "Asia/Kolkata",
  "age_banner_text": "14 weeks old",
  "avg_sleep_in_mins": 1438.71,
  "avg_day_sleep_in_mins": 589.0,
  "avg_night_sleep_in_mins": 1270.43,
  "plot_values": [
    {
      "day_sleep_in_mins": 535.0,
      "night_sleep_in_mins": 902.0,
      "total_sleep_in_mins": 1437.0,
      "date": "2026-03-06 00:00:00.000000"
    },
    {
      "day_sleep_in_mins": 610.0,
      "night_sleep_in_mins": 845.0,
      "total_sleep_in_mins": 1455.0,
      "date": "2026-03-07 00:00:00.000000"
    },
    {
      "day_sleep_in_mins": 590.0,
      "night_sleep_in_mins": 1310.0,
      "total_sleep_in_mins": 1900.0,
      "date": "2026-03-08 00:00:00.000000"
    },
    {
      "day_sleep_in_mins": 620.0,
      "night_sleep_in_mins": 1400.0,
      "total_sleep_in_mins": 2020.0,
      "date": "2026-03-09 00:00:00.000000"
    },
    {
      "day_sleep_in_mins": 540.0,
      "night_sleep_in_mins": 1280.0,
      "total_sleep_in_mins": 1820.0,
      "date": "2026-03-10 00:00:00.000000"
    },
    {
      "day_sleep_in_mins": 580.0,
      "night_sleep_in_mins": 1350.0,
      "total_sleep_in_mins": 1930.0,
      "date": "2026-03-11 00:00:00.000000"
    },
    {
      "day_sleep_in_mins": 548.0,
      "night_sleep_in_mins": 1206.0,
      "total_sleep_in_mins": 1754.0,
      "date": "2026-03-12 00:00:00.000000"
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `timezone` | string | Baby's configured timezone (e.g., `Asia/Kolkata`, `America/Los_Angeles`) |
| `age_banner_text` | string | Baby's age in weeks (e.g., `"14 weeks old"`) |
| `avg_sleep_in_mins` | number | Average total sleep per day across the queried period, in minutes |
| `avg_day_sleep_in_mins` | number | Average daytime sleep per day across the queried period, in minutes |
| `avg_night_sleep_in_mins` | number | Average nighttime sleep per day across the queried period, in minutes |
| `plot_values` | array | One entry per day in the requested range |

### Plot Value Object (per day)

| Field | Type | Description |
|-------|------|-------------|
| `day_sleep_in_mins` | number | Daytime sleep for this day, in minutes |
| `night_sleep_in_mins` | number | Nighttime sleep for this day, in minutes |
| `total_sleep_in_mins` | number | Total sleep for this day, in minutes (`day_sleep_in_mins + night_sleep_in_mins`) |
| `date` | string | The date this entry covers (`YYYY-MM-DD HH:MM:SS.ffffff`) |

All sleep values are in **minutes** (not seconds). Day/night split is determined by the baby's configured day start time.

---

## Practical Usage

### Querying a Week

Set `start_time` to the first day and `end_time` to 7 days later:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/weekly-sleep-graph?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Returns 7 entries in `plot_values`, one per day.

### Building a Weekly Summary

```python
import requests
from datetime import datetime, timedelta

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.cradlewise.com/api/v1"

# Last 7 days
end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")

resp = requests.get(f"{BASE}/sleep/weekly-sleep-graph", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

print(f"Timezone: {data['timezone']}")
print(f"Baby info: {data['age_banner_text']}")
print(f"\nAverages:")
print(f"  Total: {data['avg_sleep_in_mins'] / 60:.1f}h/day")
print(f"  Day:   {data['avg_day_sleep_in_mins'] / 60:.1f}h/day")
print(f"  Night: {data['avg_night_sleep_in_mins'] / 60:.1f}h/day")

print(f"\nDaily breakdown:")
for day in data["plot_values"]:
    date = day["date"][:10]
    total_hrs = day["total_sleep_in_mins"] / 60
    day_hrs = day["day_sleep_in_mins"] / 60
    night_hrs = day["night_sleep_in_mins"] / 60
    print(f"  {date}: {total_hrs:.1f}h total (day: {day_hrs:.1f}h, night: {night_hrs:.1f}h)")
```

Example output:
```
Timezone: Asia/Kolkata
Baby info: 14 weeks old

Averages:
  Total: 24.0h/day
  Day:   9.8h/day
  Night: 21.2h/day

Daily breakdown:
  2026-03-06: 24.0h total (day: 8.9h, night: 15.0h)
  2026-03-07: 24.3h total (day: 10.2h, night: 14.1h)
  2026-03-08: 31.7h total (day: 9.8h, night: 21.8h)
  2026-03-09: 33.7h total (day: 10.3h, night: 23.3h)
  2026-03-10: 30.3h total (day: 9.0h, night: 21.3h)
  2026-03-11: 32.2h total (day: 9.7h, night: 22.5h)
  2026-03-12: 29.2h total (day: 9.1h, night: 20.1h)
```

### Converting to Hours and Minutes

```python
def mins_to_hm(mins):
    h = int(mins // 60)
    m = int(mins % 60)
    return f"{h}h {m}m"

for day in data["plot_values"]:
    print(f"{day['date'][:10]}: {mins_to_hm(day['total_sleep_in_mins'])}")
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

### Averages vs. Daily Totals

The `avg_sleep_in_mins`, `avg_day_sleep_in_mins`, and `avg_night_sleep_in_mins` are computed across the entire queried period. They may not equal the simple average of `plot_values` entries if some days have missing or partial data.

### Future Dates

If the range includes future dates, those days will likely have zero or null values in `plot_values`. The averages will still be computed across all days in the range, potentially deflating the numbers.

### Reversed Date Range (`start_time` > `end_time`)

Likely returns `500 Internal Server Error` based on behavior of other sleep endpoints. **Always validate that `start_time < end_time` in your code.**

### Empty Results

If no sleep activity occurred during the range (e.g., crib was off), `plot_values` may contain entries with zero values. The averages may also be zero.

### Day/Night Split

The boundary between "day sleep" and "night sleep" is determined by the baby's configured day start time setting, not by a fixed hour. This is the same boundary used across all sleep endpoints.

### Units Are Minutes

Unlike C-Chart and Day Metrics (which use seconds for most duration fields), this endpoint returns all sleep values in **minutes**. Do not divide by 3600 — divide by 60 to convert to hours.

---

## Error Responses

| Status | Cause | Response |
|--------|-------|----------|
| 401 | Missing or invalid token | `{"detail": "Missing authorization header"}` or `{"detail": "Invalid token"}` |
| 403 | No Nurture Plus subscription | `{"detail": "Nurture Plus subscription required"}` |
| 422 | Missing `start_time` or `end_time` | `{"detail": [{"msg": "Field required", ...}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded"}` |
| 500 | Invalid date format (e.g., T separator) or reversed range | `Internal Server Error` |
