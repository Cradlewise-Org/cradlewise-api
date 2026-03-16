# Cradlewise API

> **Beta Notice:** This API is an early-access project built for tinkerers and developers who want to build on top of their Cradlewise crib data. It is under active development — endpoints may change, return unexpected data, or experience downtime. We share it in the spirit of openness, but please set expectations accordingly: this is a side project, not a production service with an SLA.
>
> Found a bug or have a request? Email **support@cradlewise.com** — we read everything, but may not be able to address every issue immediately.

Official REST API for accessing your baby's sleep data and real-time status from your Cradlewise smart crib.

**Available to Nurture Plus subscribers.** Generate your API token from the [Nurture web portal](https://nurture.cradlewise.com).

## Quick Start

```bash
# Get your baby's current status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.cradlewise.com/api/v1/baby/status
```

```json
{
  "status": "sleeping",
  "since": "2026-03-12T22:15:00Z",
  "is_in_crib": true,
  "crib_mode": {
    "bounce": "on",
    "music": "off"
  },
  "timestamp": "2026-03-13T01:30:00Z"
}
```

## Table of Contents

- [Authentication](#authentication)
- [Date & Time Handling](#date--time-handling)
- [Endpoints](#endpoints)
  - [Baby Status](#baby-status)
  - [Sleep Sessions (C-Chart)](#sleep-sessions-c-chart)
  - [Day Metrics](#day-metrics)
  - [Weekly Sleep Graph](#weekly-sleep-graph)
  - [Weekly Rise & Bed Time](#weekly-rise--bed-time)
  - [Weekly Nap Planner](#weekly-nap-planner)
  - [Weekly Sleep Metrics](#weekly-sleep-metrics)
  - [Weekly Longest Stretch](#weekly-longest-stretch)
  - [Monthly Sleep Graph](#monthly-sleep-graph)
  - [Monthly Rise & Bed Time](#monthly-rise--bed-time)
  - [Monthly Longest Stretch](#monthly-longest-stretch)
  - [Monthly Sleep Metrics](#monthly-sleep-metrics)
- [Rate Limits](#rate-limits)
- [Error Codes](#error-codes)
- [Examples](#examples)
- [Detailed Endpoint Documentation](#detailed-endpoint-documentation)
- [FAQ](#faq)

---

## Authentication

All requests require a Bearer token in the `Authorization` header.

```
Authorization: Bearer cw_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Getting your token:**

1. Log in to the [Nurture web portal](https://nurture.cradlewise.com)
2. Go to **API Access** in the sidebar
3. Select your baby from the dropdown
4. Click **Generate API Token**
5. Copy the token — it remains visible on the portal

**Token details:**

| Property | Value |
|----------|-------|
| Format | `cw_` + 40 hex characters |
| Validity | 1 year from creation |
| Scope | One token per baby, read-only |
| Baby ID | Resolved from token — never passed in requests |

Generating a new token automatically revokes the previous one. You can also revoke a token manually from the portal. If your Nurture Plus subscription lapses, the API returns `403` — reactivating your subscription restores access with the same token.

---

## Date & Time Handling

Sleep endpoints require `start_time` and `end_time` query parameters.

**Format:** `YYYY-MM-DD HH:MM:SS` (with a space, not `T`)

```
?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

**Important — Day Start Time:**

Cradlewise uses a configurable "day start time" per baby (visible in your app settings). This affects how sleep data is bucketed into days. For example, if the day start time is 7:00 AM:

- "March 10th" means **March 10, 7:00 AM → March 11, 7:00 AM**
- Night sleep on the 10th extends into the early morning of the 11th — this is intentional so that a single night isn't split across two days

This matches what you see in the Cradlewise app. When querying date ranges, align your `start_time` to your baby's day start time for results consistent with the app.

**Timezone:** Responses include a `timezone` field (e.g., `America/Los_Angeles`) reflecting your crib's configured timezone. All date strings in responses use this timezone.

---

## Endpoints

Base URL: `https://api.cradlewise.com`

All endpoints are `GET` requests. The baby is identified automatically from your token — no baby ID needed in the URL.

---

### Baby Status `Stable`

Real-time status of your baby. Designed for polling (up to every 30 seconds).

```
GET /api/v1/baby/status
```

**Response:**

```json
{
  "status": "sleeping",
  "since": "2026-03-12T22:15:00.000000Z",
  "is_in_crib": true,
  "crib_mode": {
    "bounce": "on",
    "music": "off"
  },
  "timestamp": "2026-03-13T01:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `sleeping`, `awake`, `crying`, `away`, `unknown` |
| `since` | string | ISO 8601 timestamp of when the current status began |
| `is_in_crib` | boolean | `false` when status is `away` |
| `crib_mode.bounce` | string | Current bounce mode (`on`, `off`, or specific level) |
| `crib_mode.music` | string | Current music/sound mode |
| `timestamp` | string | Server time when the response was generated |

**Use case:** Poll every 30s and trigger automations — mute doorbell when `sleeping`, start bottle warmer on `awake`, announce `crying` via smart speakers.

---

### Sleep Sessions (C-Chart) `Stable`

Individual sleep sessions within a date range — the most granular view of crib activity.

```
GET /api/v1/sleep/c-chart?start_time=2026-03-12 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "timezone": "America/Los_Angeles",
  "day_start_time": "2026-03-12 00:00:00.000000",
  "sessions": [
    {
      "session_id": "sess_0",
      "start_time": "2026-03-12 20:30:00.000000",
      "end_time": "2026-03-13 06:45:00.000000",
      "header": "{baby_name} was in bed for 10h 15m, slept 9h 30m",
      "is_user_added": false,
      "total_time_in_crib_in_seconds": 36900.0,
      "total_time_asleep_in_seconds": 34200.0,
      "total_time_awake_in_seconds": 2700.0
    }
  ],
  "events": [...],
  "soothe_events": [...],
  "day_aggregates": {...},
  "video_history_data": [...]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sessions[].start_time` | string | When the baby was placed in the crib |
| `sessions[].end_time` | string | When the baby was taken out |
| `sessions[].total_time_in_crib_in_seconds` | float | Total time in crib |
| `sessions[].total_time_asleep_in_seconds` | float | Time spent sleeping |
| `sessions[].total_time_awake_in_seconds` | float | Time spent awake in crib |
| `sessions[].is_user_added` | boolean | Whether this session was manually logged |
| `events` | array | Sleep/wake transition events within sessions |
| `soothe_events` | array | Bounce/sound soothe activations |

---

### Day Metrics `Stable`

Key daily metrics — soothes, wake windows, nap counts, and more for a specific day.

```
GET /api/v1/sleep/day-metrics?start_time=2026-03-12 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "header": "KEY METRICS",
  "timezone": "America/Los_Angeles",
  "metrics": [
    {
      "date": "2026-03-12 00:00:00.000000",
      "banners": [
        {
          "type": "soothes",
          "header": "SOOTHES",
          "data": {
            "value": 3,
            "display_value": "3",
            "description": "no of soothes"
          }
        },
        {
          "type": "total_sleep",
          "header": "TOTAL SLEEP",
          "data": {
            "value": 720,
            "display_value": "12h 0m",
            "description": "total sleep"
          }
        }
      ]
    }
  ]
}
```

| Banner Type | Description |
|-------------|-------------|
| `soothes` | Number of bounce/sound soothe activations |
| `total_sleep` | Total sleep duration for the day |
| `night_sleep` | Night sleep duration |
| `day_sleep` | Daytime nap duration |
| `longest_stretch` | Longest continuous sleep stretch |
| `wake_windows` | Average time between naps |
| `naps` | Number of naps |

---

### Weekly Sleep Graph `Beta`

Daily sleep totals for a week, broken down by day vs. night sleep.

```
GET /api/v1/sleep/weekly-sleep-graph?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "timezone": "America/Los_Angeles",
  "age_banner_text": "13 months old",
  "avg_sleep_in_mins": 720.0,
  "avg_day_sleep_in_mins": 180.0,
  "avg_night_sleep_in_mins": 540.0,
  "plot_values": [
    {
      "day_sleep_in_mins": 200.0,
      "night_sleep_in_mins": 560.0,
      "total_sleep_in_mins": 760.0,
      "date": "2026-03-06 00:00:00.000000"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `avg_sleep_in_mins` | float | Average total sleep per day across the range |
| `avg_day_sleep_in_mins` | float | Average daytime sleep |
| `avg_night_sleep_in_mins` | float | Average nighttime sleep |
| `plot_values[].date` | string | Day this data point represents |
| `plot_values[].total_sleep_in_mins` | float | Total sleep that day (minutes) |

---

### Weekly Rise & Bed Time `Beta`

Average and daily rise/bed times for the week.

```
GET /api/v1/sleep/weekly-rise-and-bed-time?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "day_start_time": "2026-03-06 07:00:00.000000",
  "avg_rise_time": "07:15",
  "avg_bed_time": "19:30",
  "plot_values": [
    {
      "rise_time": "07:20",
      "bed_time": "19:45",
      "date": "2026-03-06 07:00:00.000000"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `avg_rise_time` | string | Average morning wake time (HH:MM) |
| `avg_bed_time` | string | Average evening bed time (HH:MM) |
| `plot_values[].rise_time` | string | Rise time for that day (empty string if no data) |
| `plot_values[].bed_time` | string | Bed time for that day (empty string if no data) |

---

### Weekly Nap Planner `Beta`

Nap duration and wake window trends for the week.

```
GET /api/v1/sleep/weekly-nap-planner?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "day_start_time": "2026-03-06 07:00:00.000000",
  "avg_nap_duration_in_mins": 90.0,
  "avg_wake_window_in_mins": 180.0,
  "avg_day_nap_duration_in_mins": 90.0,
  "avg_night_nap_duration_in_mins": 0,
  "avg_day_wake_window_in_mins": 180.0,
  "avg_night_wake_window_in_mins": 0,
  "plot_values": [...]
}
```

---

### Weekly Sleep Metrics `Beta`

Combined weekly view — aggregates sleep graph, nap planner, rise/bed time, and longest stretch into one response.

```
GET /api/v1/sleep/weekly-sleep-metrics?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "sleep_graph_metrics": { ... },
  "nap_planner_metrics": { ... },
  "rise_and_bed_time_metrics": { ... },
  "longest_stretch_metrics": { ... }
}
```

Each sub-object contains the same data as its individual endpoint. Use this to fetch all weekly data in a single request.

---

### Weekly Longest Stretch `Beta`

Longest continuous sleep stretch per day across the week.

```
GET /api/v1/sleep/weekly-longest-stretch?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "avg_longest_stretch_in_mins": 540.0,
  "avg_longest_stretch_display_text": "9h 0m",
  "plot_values": [
    {
      "longest_stretch_in_mins": 560.0,
      "longest_stretch_in_hours": 9.3,
      "longest_stretch_display_text": "9h 20m",
      "date": "2026-03-06 07:00:00.000000"
    }
  ]
}
```

---

### Monthly Sleep Graph `Beta`

Monthly sleep totals over a longer date range.

```
GET /api/v1/sleep/monthly-sleep-graph?start_time=2026-01-01 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "age_banner_text": "13 months old",
  "plot_values": [
    {
      "day_sleep_in_mins": 180.0,
      "night_sleep_in_mins": 540.0,
      "total_sleep_in_mins": 720.0,
      "month": "2026-01-15 00:00:00.000000"
    }
  ]
}
```

The `month` field represents the month this data point covers. One entry per month in the range.

---

### Monthly Rise & Bed Time `Beta`

```
GET /api/v1/sleep/monthly-rise-and-bed-time?start_time=2026-01-01 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "plot_values": [
    {
      "rise_time": "2026-03-13 07:20:00.000000",
      "bed_time": "2026-03-13 19:30:00.000000",
      "month": "2026-03-13 00:00:00.000000"
    }
  ]
}
```

---

### Monthly Longest Stretch `Beta`

```
GET /api/v1/sleep/monthly-longest-stretch?start_time=2026-01-01 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "plot_values": [
    {
      "longest_stretch_in_mins": 540.0,
      "longest_stretch_in_hours": 9.0,
      "longest_stretch_display_text": "9h 0m",
      "month": "2026-03-13 00:00:00.000000"
    }
  ]
}
```

---

### Monthly Sleep Metrics `Beta`

Combined monthly view — all monthly metrics in one response.

```
GET /api/v1/sleep/monthly-sleep-metrics?start_time=2026-01-01 00:00:00&end_time=2026-03-13 00:00:00
```

**Response:**

```json
{
  "sleep_graph_metrics": { ... },
  "rise_and_bed_time_metrics": { ... },
  "longest_stretch_metrics": { ... },
  "avg_no_of_naps_metrics": { ... }
}
```

---

## Rate Limits

All limits are per token. Exceeding a limit returns `429 Too Many Requests`.

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/baby/status` | 2 requests | per minute |
| `/api/v1/sleep/*` | 60 requests | per hour |
| All endpoints combined | 500 requests | per day |

Response headers on `429`:

```
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1710288000
```

`X-RateLimit-Reset` is a Unix timestamp indicating when the limit resets.

**Recommended polling intervals:**

| Use Case | Interval | Daily Usage |
|----------|----------|-------------|
| Home automation (status) | Every 30s | ~2,880/day (within daily cap if limited to active hours) |
| Dashboard refresh (sleep data) | Every 15 min | ~96/day |
| Daily summary script | Once per day | 1/day |

For home automation, poll `/baby/status` every 30 seconds only during the hours your automations are active (e.g., 6 PM to 8 AM) to stay within the daily cap.

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| `200` | Success | — |
| `401` | Unauthorized | Missing or invalid token |
| `403` | Forbidden | Nurture Plus subscription required or expired |
| `404` | Not Found | No data for the requested resource |
| `422` | Validation Error | Invalid request parameters |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Server Error | Unexpected error — please report to support@cradlewise.com |

**Error response format:**

```json
{
  "detail": "Human-readable error message"
}
```

---

## Examples

### Python: Weekly Sleep Summary

```python
import requests

TOKEN = "cw_your_token_here"
BASE = "https://api.cradlewise.com/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Fetch last 7 days of sleep data
resp = requests.get(
    f"{BASE}/sleep/weekly-sleep-graph",
    headers=HEADERS,
    params={
        "start_time": "2026-03-06 00:00:00",
        "end_time": "2026-03-13 00:00:00",
    },
)
data = resp.json()

print(f"Average sleep: {data['avg_sleep_in_mins']:.0f} min/day")
for day in data["plot_values"]:
    total_hrs = day["total_sleep_in_mins"] / 60
    print(f"  {day['date'][:10]}: {total_hrs:.1f}h total")
```

### Python: Home Automation Status Poller

```python
import requests
import time

TOKEN = "cw_your_token_here"
URL = "https://api.cradlewise.com/api/v1/baby/status"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

last_status = None

while True:
    resp = requests.get(URL, headers=HEADERS)

    if resp.status_code == 429:
        reset = int(resp.headers.get("X-RateLimit-Reset", 0))
        wait = max(reset - int(time.time()), 30)
        print(f"Rate limited. Waiting {wait}s...")
        time.sleep(wait)
        continue

    data = resp.json()
    status = data["status"]

    if status != last_status:
        print(f"Status changed: {last_status} -> {status}")
        # Trigger your automation here:
        # - status == "awake"  -> turn on nightlight
        # - status == "sleeping" -> mute doorbell
        # - status == "crying" -> notify via speaker
        last_status = status

    time.sleep(30)  # Poll every 30 seconds
```

### Node.js: Fetch Baby Status

```javascript
const TOKEN = "cw_your_token_here";
const BASE = "https://api.cradlewise.com/api/v1";

async function getBabyStatus() {
  const res = await fetch(`${BASE}/baby/status`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });

  if (!res.ok) {
    console.error(`Error ${res.status}: ${(await res.json()).detail}`);
    return null;
  }

  return res.json();
}

const status = await getBabyStatus();
console.log(`Baby is ${status.status} since ${status.since}`);
```

### Home Assistant: REST Sensor

```yaml
# configuration.yaml
rest:
  - resource: https://api.cradlewise.com/api/v1/baby/status
    headers:
      Authorization: "Bearer cw_your_token_here"
    scan_interval: 30
    sensor:
      - name: "Baby Status"
        value_template: "{{ value_json.status }}"
        json_attributes:
          - since
          - is_in_crib
          - crib_mode

# automations.yaml
automation:
  - alias: "Mute doorbell when baby is sleeping"
    trigger:
      - platform: state
        entity_id: sensor.baby_status
        to: "sleeping"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.doorbell_chime

  - alias: "Turn on nightlight when baby wakes"
    trigger:
      - platform: state
        entity_id: sensor.baby_status
        to: "awake"
    action:
      - service: light.turn_on
        target:
          entity_id: light.nursery_nightlight
        data:
          brightness_pct: 10
```

### curl: Quick Reference

```bash
# Baby status
curl -H "Authorization: Bearer $TOKEN" \
  https://api.cradlewise.com/api/v1/baby/status

# Weekly sleep graph
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/weekly-sleep-graph?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"

# Day metrics for a specific day
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/day-metrics?start_time=2026-03-12%2000:00:00&end_time=2026-03-13%2000:00:00"

# Sleep sessions (c-chart) for last 24 hours
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/c-chart?start_time=2026-03-12%2000:00:00&end_time=2026-03-13%2000:00:00"

# Monthly trends (3 months)
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-sleep-metrics?start_time=2026-01-01%2000:00:00&end_time=2026-03-13%2000:00:00"
```

---

## Detailed Endpoint Documentation

Each endpoint has a comprehensive deep-dive doc with full response schemas, edge cases, practical code examples, and gotchas discovered through testing.

| Endpoint | Doc |
|----------|-----|
| Baby Status | [docs/baby-status.md](docs/baby-status.md) |
| Sleep Sessions (C-Chart) | [docs/c-chart.md](docs/c-chart.md) |
| Day Metrics | [docs/day-metrics.md](docs/day-metrics.md) |
| Weekly Sleep Graph | [docs/weekly-sleep-graph.md](docs/weekly-sleep-graph.md) |
| Weekly Rise & Bed Time | [docs/weekly-rise-and-bed-time.md](docs/weekly-rise-and-bed-time.md) |
| Weekly Nap Planner | [docs/weekly-nap-planner.md](docs/weekly-nap-planner.md) |
| Weekly Sleep Metrics | [docs/weekly-sleep-metrics.md](docs/weekly-sleep-metrics.md) |
| Weekly Longest Stretch | [docs/weekly-longest-stretch.md](docs/weekly-longest-stretch.md) |
| Monthly Sleep Graph | [docs/monthly-sleep-graph.md](docs/monthly-sleep-graph.md) |
| Monthly Rise & Bed Time | [docs/monthly-rise-and-bed-time.md](docs/monthly-rise-and-bed-time.md) |
| Monthly Longest Stretch | [docs/monthly-longest-stretch.md](docs/monthly-longest-stretch.md) |
| Monthly Sleep Metrics | [docs/monthly-sleep-metrics.md](docs/monthly-sleep-metrics.md) |

---

## FAQ

**Can I control the crib via the API?**
No. The API is read-only. You can read baby status and sleep data, but cannot control bounce, sound, or any crib settings.

**What happens if my Nurture Plus subscription expires?**
The API returns `403 Forbidden`. Your token is not deleted — reactivating your subscription restores access immediately with the same token.

**Can I have multiple tokens for the same baby?**
No. One active token per baby. Generating a new token revokes the previous one.

**How quickly does the baby status update?**
Status is based on the latest sleep event from the crib. It typically updates within seconds of a state change (baby placed in crib, falls asleep, wakes up, picked up).

**Is my data safe?**
- Tokens are read-only and scoped to a single baby
- No personally identifiable information (PII) is returned — no parent names, emails, or addresses
- Token hashes are stored in the database, not raw tokens
- HTTPS only

**My automation needs faster updates than 30s polling. Is there a push option?**
Not yet. Webhooks and real-time push notifications are on our roadmap. For now, 30-second polling covers all identified home automation use cases (doorbell mute, nightlight, bottle warmer).

**Can I use this with ChatGPT / Claude / other AI tools?**
Yes — paste this README into any AI assistant and ask it to build integrations for you. The API is designed to be AI-parseable. An MCP (Model Context Protocol) server is on our roadmap for native AI tool integration.

**I found a bug or have a feature request.**
Email **support@cradlewise.com**. We read everything, but this is a side project to support tinkerers — we may not be able to address every issue or request immediately.

**What does "Beta" mean on an endpoint?**
Beta endpoints are functional but still being refined. Response schemas, field names, or data accuracy may change without notice. Stable endpoints have a locked schema and are safe to build automations on.

**Is there an SLA or uptime guarantee?**
No. This API is provided as-is, without guarantees around uptime, latency, or data accuracy. It runs on the same infrastructure as our internal tools, but is not monitored to production standards.

---

## Endpoint Quick Reference

| Method | Endpoint | Params | Status | Description |
|--------|----------|--------|--------|-------------|
| GET | `/api/v1/baby/status` | — | Stable | Real-time baby status |
| GET | `/api/v1/sleep/c-chart` | `start_time`, `end_time` | Stable | Individual sleep sessions |
| GET | `/api/v1/sleep/day-metrics` | `start_time`, `end_time` | Stable | Daily key metrics |
| GET | `/api/v1/sleep/weekly-sleep-graph` | `start_time`, `end_time` | Beta | Daily sleep totals (week) |
| GET | `/api/v1/sleep/weekly-rise-and-bed-time` | `start_time`, `end_time` | Beta | Rise/bed times (week) |
| GET | `/api/v1/sleep/weekly-nap-planner` | `start_time`, `end_time` | Beta | Nap/wake windows (week) |
| GET | `/api/v1/sleep/weekly-sleep-metrics` | `start_time`, `end_time` | Beta | All weekly metrics combined |
| GET | `/api/v1/sleep/weekly-longest-stretch` | `start_time`, `end_time` | Beta | Longest sleep stretch (week) |
| GET | `/api/v1/sleep/monthly-sleep-graph` | `start_time`, `end_time` | Beta | Monthly sleep totals |
| GET | `/api/v1/sleep/monthly-rise-and-bed-time` | `start_time`, `end_time` | Beta | Rise/bed times (monthly) |
| GET | `/api/v1/sleep/monthly-longest-stretch` | `start_time`, `end_time` | Beta | Longest stretch (monthly) |
| GET | `/api/v1/sleep/monthly-sleep-metrics` | `start_time`, `end_time` | Beta | All monthly metrics combined |

---

*Built by Cradlewise for tinkerers and developers. First baby monitor company with a public API.*
