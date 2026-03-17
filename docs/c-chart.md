# Sleep Sessions (C-Chart)

Detailed sleep session data for your baby — every session's start/end times, durations, individual sleep/wake events within sessions, and daily aggregates. This is the richest endpoint for building sleep dashboards or analyzing sleep patterns.

## Request

```
GET /api/v1/sleep/c-chart
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
  "https://integrations.cradlewise.com/api/v1/sleep/c-chart?start_time=2026-03-10%2000:00:00&end_time=2026-03-11%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### Single-Day Example

```json
{
  "timezone": "Asia/Kolkata",
  "day_start_time": "2026-03-13 00:00:00.000000",
  "sessions": [
    {
      "session_id": "sess_0",
      "start_time": "2026-03-09 10:47:17.614567",
      "end_time": "2026-03-10 03:48:34.314255",
      "header": "Baby was in bed for {total_crib_time}, slept {total_nap_time}",
      "is_user_added": false,
      "total_time_in_crib_in_seconds": 61276.699688,
      "total_time_asleep_in_seconds": 61276.699688,
      "total_time_awake_in_seconds": 0
    },
    {
      "session_id": "sess_1",
      "start_time": "2026-03-10 16:52:35.551858",
      "end_time": "2026-03-11 03:41:45.076413",
      "header": "Baby was in bed for {total_crib_time}, slept {total_nap_time}",
      "is_user_added": false,
      "total_time_in_crib_in_seconds": 38949.524555,
      "total_time_asleep_in_seconds": 38949.524555,
      "total_time_awake_in_seconds": 0
    }
  ],
  "events": [
    {
      "event_name": "deep_sleep",
      "event_label": "sleep",
      "event_value": "5",
      "event_time": "2026-03-09 10:42:42.486880",
      "is_user_added": false
    },
    {
      "event_name": "quiet_awake",
      "event_label": "stirring",
      "event_value": "3",
      "event_time": "2026-03-09 10:42:49.462890",
      "is_user_added": false
    }
  ],
  "soothe_events": [],
  "day_aggregates": {
    "2026-03-10 00:00:00.000000": {
      "total_time_in_crib_in_seconds": 72615.09,
      "total_time_asleep_in_seconds": 72615.09,
      "total_time_awake_in_seconds": 0,
      "total_day_sleep": 0,
      "total_night_sleep": 72615.09
    }
  },
  "video_history_data": []
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `timezone` | string | Baby's configured timezone (e.g., `Asia/Kolkata`, `America/Los_Angeles`) |
| `day_start_time` | string | The baby's configured "day start" boundary. Sleep data is bucketed into days relative to this time |
| `sessions` | array | Sleep sessions within the requested window |
| `events` | array | Individual sleep/wake state transitions (granular timeline) |
| `soothe_events` | array | Crib soothing events (bounce/music activations). May be empty |
| `day_aggregates` | object | Daily totals keyed by date string |
| `video_history_data` | array | Video recording references. May be empty |

### Session Object

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Sequential ID like `sess_0`, `sess_1`, etc. |
| `start_time` | string | When the session began (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `end_time` | string | When the session ended |
| `header` | string | Template string with placeholders `{total_crib_time}`, `{total_nap_time}` |
| `is_user_added` | boolean | `true` if the session was manually logged by the parent |
| `total_time_in_crib_in_seconds` | number | Total duration baby was in the crib during this session |
| `total_time_asleep_in_seconds` | number | Total sleep time within this session |
| `total_time_awake_in_seconds` | number | Total awake time within this session |

### Event Object

| Field | Type | Description |
|-------|------|-------------|
| `event_name` | string | Granular state — see Event Types table below |
| `event_label` | string | High-level category — see Event Types table below |
| `event_value` | string | Numeric code (as string) — see Event Types table below |
| `event_time` | string | When this state transition occurred |
| `is_user_added` | boolean | `true` if manually logged |

### Event Types

| `event_name` | `event_label` | `event_value` | Description |
|--------------|---------------|---------------|-------------|
| `deep_sleep` | `sleep` | `5` | Baby is in deep sleep |
| `light_sleep` | `sleep` | `4` | Baby is in light sleep |
| `quiet_awake` | `stirring` | `3` | Baby is stirring / lightly awake |
| `active_awake` | `awake` | `2` | Baby is actively awake |
| `away` | `away` | `1` | Baby removed from crib |

### Day Aggregates

Keyed by date string in `YYYY-MM-DD HH:MM:SS.ffffff` format.

| Field | Type | Description |
|-------|------|-------------|
| `total_time_in_crib_in_seconds` | number | Total time baby was in the crib that day |
| `total_time_asleep_in_seconds` | number | Total sleep time that day |
| `total_time_awake_in_seconds` | number | Total awake-in-crib time that day |
| `total_day_sleep` | number | Daytime sleep in seconds |
| `total_night_sleep` | number | Nighttime sleep in seconds |

Day/night split is determined by the baby's `day_start_time` setting.

---

## Date Format

**Use space-separated format only:**

| Format | Works? |
|--------|--------|
| `2026-03-10 00:00:00` | Yes |
| `2026-03-10%2000:00:00` | Yes (URL-encoded space) |
| `2026-03-10T00:00:00` | **No** — returns `500 Internal Server Error` |

This applies to all sleep endpoints, not just C-Chart.

---

## Practical Usage

### Querying a Single Day

Set `start_time` to midnight and `end_time` to the next midnight:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/c-chart?start_time=2026-03-10%2000:00:00&end_time=2026-03-11%2000:00:00"
```

Note: Sessions that **span midnight** are included if any part falls within the window. A session starting at 10:47 PM on March 9th and ending at 3:48 AM on March 10th will appear in a March 10 query.

### Querying Multiple Days

```bash
# 7 days
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/c-chart?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

Typical results for a 7-day window: ~9 sessions, ~16 events, 7 day_aggregate entries.

### Sub-Day Windows

You can query any time window, not just full days:

```bash
# 1-hour window
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/c-chart?start_time=2026-03-10%2002:00:00&end_time=2026-03-10%2003:00:00"
```

Returns sessions active during that hour.

### Calculating Sleep Duration

```python
for session in data["sessions"]:
    hours = session["total_time_asleep_in_seconds"] / 3600
    print(f"Session {session['session_id']}: {hours:.1f}h asleep")
```

### Using the Header Template

The `header` field contains placeholders. Replace them with your own values:

```python
header = session["header"]
crib_hrs = session["total_time_in_crib_in_seconds"] / 3600
sleep_hrs = session["total_time_asleep_in_seconds"] / 3600
text = header.replace("{total_crib_time}", f"{crib_hrs:.1f}h") \
             .replace("{total_nap_time}", f"{sleep_hrs:.1f}h")
# "Baby was in bed for 17.0h, slept 17.0h"
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

### Sessions Spanning the Query Boundary

A session that started before your `start_time` but ended within the window **is included**. The session's `start_time` may be earlier than your query's `start_time`. This is correct — you're seeing the full session, not a truncated slice.

### Events Outside the Session Window

The `events` array may include events with timestamps slightly outside the requested window. This happens because the API returns the last known event before the window as context. The first event in the array is often a "carry-forward" from before the window opened.

### Empty Results

If no sleep activity occurred during the window:
- `sessions`: empty array `[]`
- `events`: may contain 1 stale event (the last known state before the window)
- `day_aggregates`: empty object `{}`

This happens with future dates, very old dates, or periods when the crib was off.

### Reversed Date Range (`start_time` > `end_time`)

Returns `200 OK` with empty sessions and a few stale events. **No error is raised.** Always validate that `start_time < end_time` in your code.

### Zero-Width Range (`start_time` == `end_time`)

May return 1 session (data from the preceding period). This is an artifact — use a proper time window instead.

### Large Date Ranges

A 30-day query returns ~39 sessions and ~1,400 events (~200 KB response). The API handles this fine, but for dashboard rendering consider querying 7 days at a time.

### Invalid Date Strings

Non-date strings (e.g., `start_time=invalid`) return `500 Internal Server Error`. Always validate inputs before sending.

### `day_start_time` Field

This reflects the baby's configured day boundary — it's **not** your query's start time. It always shows the current setting, regardless of what time range you query. Used internally to split sleep into day vs. night totals in `day_aggregates`.

### `video_history_data`

Contains references to video recordings if the crib captured clips during the session. May be empty if video recording is disabled or if no clips were saved during the queried period.

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

# Last 24 hours
end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=1)

fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")

resp = requests.get(f"{BASE}/sleep/c-chart", headers=HEADERS, params={
    "start_time": fmt(start),
    "end_time": fmt(end),
})
data = resp.json()

print(f"Timezone: {data['timezone']}")
print(f"Sessions: {len(data['sessions'])}")

for session in data["sessions"]:
    crib_hrs = session["total_time_in_crib_in_seconds"] / 3600
    sleep_hrs = session["total_time_asleep_in_seconds"] / 3600
    print(f"\n  {session['session_id']}: {session['start_time']} → {session['end_time']}")
    print(f"    In crib: {crib_hrs:.1f}h | Asleep: {sleep_hrs:.1f}h")

# Daily totals
for date, agg in data.get("day_aggregates", {}).items():
    total = agg["total_time_asleep_in_seconds"] / 3600
    day = agg["total_day_sleep"] / 3600
    night = agg["total_night_sleep"] / 3600
    print(f"\n  {date[:10]}: {total:.1f}h total (day: {day:.1f}h, night: {night:.1f}h)")
```
