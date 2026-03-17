# Weekly Sleep Metrics `Beta`

> **Beta:** This endpoint is functional but still being refined. Response schema or data accuracy may change without notice.

Composite endpoint that combines sleep graph and nap planner data into a single response — weekly sleep totals with day/night breakdown plus individual nap-level detail. This is the most convenient endpoint for building a full weekly sleep dashboard in one call instead of hitting `weekly-sleep-graph` and `weekly-nap-planner` separately.

## Request

```
GET /api/v1/sleep/weekly-sleep-metrics
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
  "https://integrations.cradlewise.com/api/v1/sleep/weekly-sleep-metrics?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### 7-Day Example

```json
{
  "sleep_graph_metrics": {
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
      }
    ]
  },
  "nap_planner_metrics": {
    "day_start_time": "2026-03-06 00:00:00.000000",
    "avg_nap_duration_in_mins": 589.0,
    "avg_day_wake_window_in_mins": 2.0,
    "avg_naps_per_day": 1.0,
    "plot_values": [
      {
        "start_time": "2026-03-06 00:00:00.000000",
        "end_time": "2026-03-06 08:55:01.548644",
        "is_night_sleep": false,
        "is_longest_stretch": false,
        "duration_in_mins": 535.0
      },
      {
        "start_time": "2026-03-06 18:30:00.000000",
        "end_time": "2026-03-07 04:12:33.102847",
        "is_night_sleep": true,
        "is_longest_stretch": true,
        "duration_in_mins": 582.55
      }
    ]
  }
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `sleep_graph_metrics` | object | Weekly sleep totals with day/night breakdown. Same shape as the `weekly-sleep-graph` endpoint response |
| `nap_planner_metrics` | object | Individual sleep segments with nap averages. Similar to the `weekly-nap-planner` endpoint but includes `avg_naps_per_day` |

### `sleep_graph_metrics` Object

| Field | Type | Description |
|-------|------|-------------|
| `timezone` | string | Baby's configured timezone (e.g., `Asia/Kolkata`, `America/Los_Angeles`) |
| `age_banner_text` | string | Display-ready age string (e.g., `"14 weeks old"`) |
| `avg_sleep_in_mins` | number | Average total sleep per day across the queried window (minutes) |
| `avg_day_sleep_in_mins` | number | Average daytime sleep per day (minutes) |
| `avg_night_sleep_in_mins` | number | Average nighttime sleep per day (minutes) |
| `plot_values` | array | One entry per day with day/night/total breakdown |

### `sleep_graph_metrics.plot_values[]`

| Field | Type | Description |
|-------|------|-------------|
| `day_sleep_in_mins` | number | Daytime sleep for that day (minutes) |
| `night_sleep_in_mins` | number | Nighttime sleep for that day (minutes) |
| `total_sleep_in_mins` | number | Total sleep for that day (minutes) |
| `date` | string | Day boundary (`YYYY-MM-DD HH:MM:SS.ffffff`) |

### `nap_planner_metrics` Object

| Field | Type | Description |
|-------|------|-------------|
| `day_start_time` | string | The baby's configured day boundary (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `avg_nap_duration_in_mins` | number | Average nap duration across the queried window (minutes) |
| `avg_day_wake_window_in_mins` | number | Average wake window between daytime naps (minutes) |
| `avg_naps_per_day` | number | Average number of naps per day across the queried window |
| `plot_values` | array | Individual sleep segments — each nap or night sleep stretch |

### `nap_planner_metrics.plot_values[]`

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | string | When the sleep segment began (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `end_time` | string | When the sleep segment ended |
| `is_night_sleep` | boolean | `true` if this segment is classified as night sleep |
| `is_longest_stretch` | boolean | `true` if this is the longest uninterrupted sleep stretch in the period |
| `duration_in_mins` | number | Duration of this sleep segment (minutes) |

---

## Relationship to Other Endpoints

This endpoint is a composite of two standalone endpoints:

| Standalone Endpoint | Equivalent Section | Differences |
|--------------------|--------------------|-------------|
| `GET /api/v1/sleep/weekly-sleep-graph` | `sleep_graph_metrics` | Identical shape |
| `GET /api/v1/sleep/weekly-nap-planner` | `nap_planner_metrics` | Composite adds `avg_naps_per_day` field |

Use `weekly-sleep-metrics` when you need both datasets — it saves one API call and counts as a single request against rate limits. Use the standalone endpoints if you only need one half of the data.

---

## Date Format

**Use space-separated format only:**

| Format | Works? |
|--------|--------|
| `2026-03-06 00:00:00` | Yes |
| `2026-03-06%2000:00:00` | Yes (URL-encoded space) |
| `2026-03-06T00:00:00` | **No** — returns `500 Internal Server Error` |

This applies to all sleep endpoints, not just weekly-sleep-metrics.

---

## Practical Usage

### Querying a Full Week

Set `start_time` to 7 days ago at midnight and `end_time` to today at midnight:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/weekly-sleep-metrics?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Typical results: 7 entries in `sleep_graph_metrics.plot_values` (one per day) and ~20-30 entries in `nap_planner_metrics.plot_values` (one per sleep segment).

### Building a Weekly Sleep Chart

```python
for day in data["sleep_graph_metrics"]["plot_values"]:
    date = day["date"][:10]
    total_hrs = day["total_sleep_in_mins"] / 60
    day_hrs = day["day_sleep_in_mins"] / 60
    night_hrs = day["night_sleep_in_mins"] / 60
    print(f"{date}: {total_hrs:.1f}h total (day: {day_hrs:.1f}h, night: {night_hrs:.1f}h)")
```

### Extracting the Longest Stretch

```python
longest = next(
    (s for s in data["nap_planner_metrics"]["plot_values"] if s["is_longest_stretch"]),
    None
)
if longest:
    hrs = longest["duration_in_mins"] / 60
    print(f"Longest stretch: {hrs:.1f}h ({'night' if longest['is_night_sleep'] else 'day'})")
```

### Counting Naps vs. Night Sleeps

```python
naps = [s for s in data["nap_planner_metrics"]["plot_values"] if not s["is_night_sleep"]]
nights = [s for s in data["nap_planner_metrics"]["plot_values"] if s["is_night_sleep"]]
print(f"Naps: {len(naps)} | Night sleeps: {len(nights)}")
print(f"Avg naps/day: {data['nap_planner_metrics']['avg_naps_per_day']}")
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

Since this endpoint returns data equivalent to two calls, prefer it over calling `weekly-sleep-graph` and `weekly-nap-planner` separately to conserve rate limit budget.

---

## Edge Cases

### Empty Results

If no sleep activity occurred during the window:
- `sleep_graph_metrics.plot_values`: empty array `[]`
- `nap_planner_metrics.plot_values`: empty array `[]`
- Averages may be `0` or `null`

This happens with future dates, very old dates, or periods when the crib was off.

### Reversed Date Range (`start_time` > `end_time`)

Returns `200 OK` with empty plot values and zeroed averages. **No error is raised.** Always validate that `start_time < end_time` in your code.

### Partial Weeks

You can query fewer or more than 7 days. The averages adjust to the actual number of days with data. A 3-day query returns 3 entries in `sleep_graph_metrics.plot_values`.

### All Durations in Minutes

Unlike `c-chart` and `day-metrics` (which use seconds), this endpoint reports all durations in **minutes**. Do not divide by 60 expecting seconds — the values are already in minutes.

### `avg_sleep_in_mins` vs. Sum of Day + Night

`avg_sleep_in_mins` may not equal `avg_day_sleep_in_mins + avg_night_sleep_in_mins` exactly due to rounding. The per-day `total_sleep_in_mins` in `plot_values` may also differ slightly from `day_sleep_in_mins + night_sleep_in_mins` for the same reason.

### `day_start_time` Field

This reflects the baby's configured day boundary — it is **not** your query's start time. It always shows the current setting, regardless of what time range you query. Used internally to split sleep into day vs. night.

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

resp = requests.get(f"{BASE}/sleep/weekly-sleep-metrics", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

# Sleep graph summary
graph = data["sleep_graph_metrics"]
print(f"Timezone: {graph['timezone']}")
print(f"{graph['age_banner_text']}")
print(f"Avg total sleep: {graph['avg_sleep_in_mins'] / 60:.1f}h")
print(f"Avg day sleep: {graph['avg_day_sleep_in_mins'] / 60:.1f}h")
print(f"Avg night sleep: {graph['avg_night_sleep_in_mins'] / 60:.1f}h")

for day in graph["plot_values"]:
    date = day["date"][:10]
    total = day["total_sleep_in_mins"] / 60
    print(f"  {date}: {total:.1f}h")

# Nap planner summary
naps = data["nap_planner_metrics"]
print(f"\nAvg nap duration: {naps['avg_nap_duration_in_mins']:.0f} min")
print(f"Avg wake window: {naps['avg_day_wake_window_in_mins']:.0f} min")
print(f"Avg naps/day: {naps['avg_naps_per_day']:.1f}")

for segment in naps["plot_values"]:
    kind = "Night" if segment["is_night_sleep"] else "Nap"
    longest = " (longest)" if segment["is_longest_stretch"] else ""
    hrs = segment["duration_in_mins"] / 60
    print(f"  {kind}: {segment['start_time'][:16]} → {segment['end_time'][:16]} ({hrs:.1f}h){longest}")
```
