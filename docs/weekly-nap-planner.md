# Weekly Nap Planner

Aggregated nap and sleep data over a multi-day window — average durations, wake windows, and individual sleep segments with day/night classification. Use this endpoint to build weekly sleep summaries, track nap trends, or identify the longest uninterrupted sleep stretch.

## Request

```
GET /api/v1/sleep/weekly-nap-planner
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
  "https://api.cradlewise.com/api/v1/sleep/weekly-nap-planner?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### 7-Day Example

```json
{
  "day_start_time": "2026-03-06 02:30:00.000000",
  "avg_nap_duration_in_mins": 3513.42,
  "avg_wake_window_in_mins": 0,
  "avg_day_nap_duration_in_mins": 4279.63,
  "avg_night_nap_duration_in_mins": 1981.0,
  "avg_day_wake_window_in_mins": 0,
  "avg_night_wake_window_in_mins": 0,
  "plot_values": [
    {
      "start_time": "2026-02-27 14:08:22.317788",
      "end_time": "2026-03-06 08:55:01.548644",
      "is_night_sleep": false,
      "is_longest_stretch": false,
      "duration_in_mins": 9766.0
    },
    {
      "start_time": "2026-03-06 08:57:18.225433",
      "end_time": "2026-03-07 02:30:00.000000",
      "is_night_sleep": true,
      "is_longest_stretch": false,
      "duration_in_mins": 1052.0
    },
    {
      "start_time": "2026-03-13 07:22:10.211661",
      "end_time": "2026-03-13 14:52:14.839627",
      "is_night_sleep": true,
      "is_longest_stretch": false,
      "duration_in_mins": 450.0
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `day_start_time` | string | The baby's configured "day start" boundary (`YYYY-MM-DD HH:MM:SS.ffffff`). Sleep segments are classified as day or night relative to this time |
| `avg_nap_duration_in_mins` | number | Average nap/sleep duration across all segments in the window (minutes) |
| `avg_wake_window_in_mins` | number | Average time between sleep segments across all segments (minutes). May be `0` if not enough gaps to compute |
| `avg_day_nap_duration_in_mins` | number | Average duration of daytime naps only (minutes) |
| `avg_night_nap_duration_in_mins` | number | Average duration of nighttime sleep only (minutes) |
| `avg_day_wake_window_in_mins` | number | Average wake window between daytime naps (minutes) |
| `avg_night_wake_window_in_mins` | number | Average wake window between nighttime sleep segments (minutes) |
| `plot_values` | array | Individual nap/sleep segments within (or overlapping) the requested window |

### Plot Value Object

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | string | When the sleep segment began (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `end_time` | string | When the sleep segment ended |
| `is_night_sleep` | boolean | `true` if this segment falls within the nighttime window (based on `day_start_time`) |
| `is_longest_stretch` | boolean | `true` if this is the longest uninterrupted sleep period in the response |
| `duration_in_mins` | number | Duration of this segment in **minutes** |

---

## Date Format

**Use space-separated format only:**

| Format | Works? |
|--------|--------|
| `2026-03-06 00:00:00` | Yes |
| `2026-03-06%2000:00:00` | Yes (URL-encoded space) |
| `2026-03-06T00:00:00` | **No** — returns `500 Internal Server Error` |

This applies to all sleep endpoints, not just Weekly Nap Planner.

---

## Practical Usage

### Querying a Full Week

Set `start_time` to the beginning of the week and `end_time` to 7 days later:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/weekly-nap-planner?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Note: Segments that **started before** your `start_time` but ended within the window are included. A segment starting February 27th may appear in a March 6–13 query. This is correct — you're seeing the full segment, not a truncated slice.

### Finding the Longest Sleep Stretch

```python
longest = next(
    (seg for seg in data["plot_values"] if seg["is_longest_stretch"]),
    None
)
if longest:
    hours = longest["duration_in_mins"] / 60
    print(f"Longest stretch: {hours:.1f}h ({longest['start_time']} → {longest['end_time']})")
else:
    # Fallback: find it manually
    longest = max(data["plot_values"], key=lambda s: s["duration_in_mins"])
    hours = longest["duration_in_mins"] / 60
    print(f"Longest stretch: {hours:.1f}h")
```

### Calculating Wake Windows Between Naps

The `avg_wake_window_in_mins` field may be `0` when the API cannot compute gaps. Calculate manually from `plot_values`:

```python
from datetime import datetime

segments = sorted(data["plot_values"], key=lambda s: s["start_time"])
wake_gaps = []

for i in range(1, len(segments)):
    prev_end = datetime.strptime(segments[i - 1]["end_time"], "%Y-%m-%d %H:%M:%S.%f")
    curr_start = datetime.strptime(segments[i]["start_time"], "%Y-%m-%d %H:%M:%S.%f")
    gap_mins = (curr_start - prev_end).total_seconds() / 60
    if gap_mins > 0:
        wake_gaps.append(gap_mins)

if wake_gaps:
    avg_wake = sum(wake_gaps) / len(wake_gaps)
    print(f"Average wake window: {avg_wake:.0f} mins ({avg_wake / 60:.1f}h)")
    print(f"Longest wake window: {max(wake_gaps):.0f} mins")
```

### Separating Day vs Night Segments

```python
day_naps = [s for s in data["plot_values"] if not s["is_night_sleep"]]
night_sleeps = [s for s in data["plot_values"] if s["is_night_sleep"]]

day_total = sum(s["duration_in_mins"] for s in day_naps) / 60
night_total = sum(s["duration_in_mins"] for s in night_sleeps) / 60

print(f"Day naps: {len(day_naps)} segments, {day_total:.1f}h total")
print(f"Night sleep: {len(night_sleeps)} segments, {night_total:.1f}h total")
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

### Segments Spanning the Query Boundary

A segment that started before your `start_time` but ended within the window **is included** with its original `start_time`. In the example above, a segment starting February 27th appears in a March 6–13 query. The `duration_in_mins` reflects the full segment, not the portion within your window.

### Variable Number of Segments

Unlike endpoints that return one entry per day, `plot_values` contains a **variable number of segments**. A 7-day query might return 3 segments or 30, depending on the baby's sleep patterns. Do not assume one segment per day.

### Segments Spanning Multiple Days

A single segment can span multiple days. A segment with `duration_in_mins: 9766` is ~6.8 days. This typically indicates the crib was tracking continuous sleep/presence over an extended period.

### `is_longest_stretch` May Be All False

If no segment is flagged as the longest stretch, find it manually by sorting `plot_values` by `duration_in_mins`.

### Wake Window Averages at Zero

The `avg_wake_window_in_mins`, `avg_day_wake_window_in_mins`, and `avg_night_wake_window_in_mins` fields may all be `0`. This happens when the API cannot determine gaps between segments — calculate wake windows manually from `plot_values` (see Practical Usage above).

### Empty Results

If no sleep activity occurred during the window:
- `plot_values`: empty array `[]`
- Averages: `0` or absent

This happens with future dates, very old dates, or periods when the crib was off.

### `day_start_time` Field

This reflects the baby's configured day boundary — it's **not** your query's start time. It always shows the current setting, regardless of what time range you query. Used internally to classify segments as day or night sleep.

### Duration Units

All duration fields are in **minutes**, not seconds. This differs from the C-Chart endpoint which uses seconds. Always check units when combining data across endpoints.

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

# Last 7 days
end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")

resp = requests.get(f"{BASE}/sleep/weekly-nap-planner", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

print(f"Day start: {data['day_start_time']}")
print(f"Avg nap duration: {data['avg_nap_duration_in_mins']:.0f} mins ({data['avg_nap_duration_in_mins'] / 60:.1f}h)")
print(f"Avg wake window: {data['avg_wake_window_in_mins']:.0f} mins")
print(f"Avg day nap: {data['avg_day_nap_duration_in_mins']:.0f} mins")
print(f"Avg night sleep: {data['avg_night_nap_duration_in_mins']:.0f} mins")

# Individual segments
segments = sorted(data["plot_values"], key=lambda s: s["start_time"])
for seg in segments:
    hours = seg["duration_in_mins"] / 60
    kind = "Night" if seg["is_night_sleep"] else "Day"
    longest = " [LONGEST]" if seg["is_longest_stretch"] else ""
    print(f"\n  {kind}: {seg['start_time']} → {seg['end_time']}")
    print(f"    Duration: {hours:.1f}h ({seg['duration_in_mins']:.0f} mins){longest}")

# Calculate wake windows manually
wake_gaps = []
for i in range(1, len(segments)):
    prev_end = datetime.strptime(segments[i - 1]["end_time"], "%Y-%m-%d %H:%M:%S.%f")
    curr_start = datetime.strptime(segments[i]["start_time"], "%Y-%m-%d %H:%M:%S.%f")
    gap_mins = (curr_start - prev_end).total_seconds() / 60
    if gap_mins > 0:
        wake_gaps.append(gap_mins)
        print(f"\n  Wake gap: {gap_mins:.0f} mins ({gap_mins / 60:.1f}h)")

if wake_gaps:
    print(f"\nCalculated avg wake window: {sum(wake_gaps) / len(wake_gaps):.0f} mins")
```
