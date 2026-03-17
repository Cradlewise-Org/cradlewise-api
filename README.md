# Cradlewise API

> **Beta Notice:** This API is an early-access project built for tinkerers and developers who want to build on top of their Cradlewise crib data. It is under active development — endpoints may change, return unexpected data, or experience downtime. We share it in the spirit of openness, but please set expectations accordingly: this is a side project, not a production service with an SLA.
>
> Found a bug or have a request? Email **support@cradlewise.com** — we read everything, but may not be able to address every issue immediately.

Official REST API for accessing your baby's sleep data and real-time status from your Cradlewise smart crib.

**Available to Nurture Plus subscribers.** During beta, tokens are provided directly by the Cradlewise team.

## Quick Start

```bash
# Get your baby's current status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://integrations.cradlewise.com/api/v1/baby/status
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
- [No Data Responses](#no-data-responses)
- [Rate Limits](#rate-limits)
- [Error Codes](#error-codes)
- [Examples](#examples)
- [Detailed Endpoint Documentation](#detailed-endpoint-documentation)
- [Roadmap](#roadmap)
- [Versioning](#versioning)
- [Changelog](#changelog)
- [FAQ](#faq)

---

## Authentication

All requests require a Bearer token in the `Authorization` header.

```
Authorization: Bearer cw_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Getting your token:**

During the beta, API tokens are generated and shared directly by the Cradlewise team. If you're interested in API access, email **support@cradlewise.com**.

> **Coming Soon:** Self-service token generation from the [Nurture web portal](https://mycrib.cradlewise.com). You'll be able to go to **API Access** in the sidebar, select your baby, and generate a token yourself. This is not yet available.

**Token details:**

| Property | Value |
|----------|-------|
| Format | `cw_` + 40 hex characters |
| Validity | 1 year from creation |
| Scope | One token per baby, read-only |
| Baby ID | Resolved from token — never passed in requests |

Generating a new token automatically revokes the previous one. If your Nurture Plus subscription lapses, the API returns `403` — reactivating your subscription restores access with the same token.

---

## Date & Time Handling

Sleep endpoints require `start_time` and `end_time` query parameters.

**Format:** `YYYY-MM-DD HH:MM:SS` (with a space, not `T`)

```
?start_time=2026-03-06 00:00:00&end_time=2026-03-13 00:00:00
```

> **Note:** When using `curl` or passing dates in URLs, the space between the date and time must be URL-encoded as `%20`. The curl examples in this README already include this encoding.

**Important — Day Start Time:**

Cradlewise uses a configurable "day start time" per baby (visible in your app settings). This affects how sleep data is bucketed into days. For example, if the day start time is 7:00 AM:

- "March 10th" means **March 10, 7:00 AM → March 11, 7:00 AM**
- Night sleep on the 10th extends into the early morning of the 11th — this is intentional so that a single night isn't split across two days

This matches what you see in the Cradlewise app. When querying date ranges, align your `start_time` to your baby's day start time for results consistent with the app.

**Timezone:** Responses include a `timezone` field (e.g., `America/Los_Angeles`) reflecting your crib's configured timezone. All date strings in responses use this timezone.

---

## Endpoints

Base URL: `https://integrations.cradlewise.com`

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

The `unknown` status may appear briefly when the crib is processing sensor data or during transitions. It can coexist with `is_in_crib: true` — this means the baby is detected in the crib but the sleep state hasn't been determined yet.

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

> **Note:** The response may include events and sessions that started before your `start_time`. This happens in two cases: (1) a session that overlaps your query window is returned whole, not truncated at boundaries, and (2) on days with no crib activity, the API may return the most recent prior event for context. Filter by timestamp on your end if you need strict date boundaries.

> **Note:** The `video_history_data` array contains thumbnail URLs on an internal domain. These URLs may not be accessible externally and are not part of the supported API surface. Do not build integrations against this field.

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
          "type": "info",
          "header": "LONGEST STRETCH",
          "data": {
            "value": 540,
            "display_value": "9h 0m",
            "description": "longest stretch"
          }
        }
      ]
    }
  ]
}
```

**Banners:** Use the `header` field to identify each metric. The `type` field is not unique — most banners use `type: "info"` as a generic value.

| Banner `header` | `type` | Description |
|-----------------|--------|-------------|
| `SOOTHES` | `soothes` | Number of bounce/sound soothe activations |
| `RISE TIME` | `info` | Morning wake time |
| `BED TIME` | `info` | Evening bed time |
| `NAPS` | `naps` | Number of naps |
| `LONGEST STRETCH` | `info` | Longest continuous sleep stretch |
| `TIME IN BED` | `info` | Total time spent in crib |
| `AWAKE IN BED` | `info` | Time spent awake while in crib |

> **Important:** Always key off the `header` string (e.g., `"LONGEST STRETCH"`) rather than `type` when parsing banners programmatically. The `type` field is not reliable for identification.

---

## No Data Responses

When querying a date range with no crib activity, endpoints still return `200` but with empty or null data. Here's what to expect:

**c-chart** — empty `sessions` array, but may include a stale event from the most recent prior session:

```json
{
  "timezone": "America/Los_Angeles",
  "sessions": [],
  "events": [
    {
      "start_time": "2026-03-13 06:45:00.000000",
      "description": "picked up"
    }
  ],
  "soothe_events": [],
  "day_aggregates": {}
}
```

**day-metrics** — banners with `null` values and empty strings:

```json
{
  "metrics": [
    {
      "date": "2026-03-17 00:00:00.000000",
      "banners": [
        {
          "type": "info",
          "header": "LONGEST STRETCH",
          "data": {
            "value": null,
            "display_value": "",
            "description": "longest stretch"
          }
        }
      ]
    }
  ]
}
```

**baby/status** — always returns current status regardless of crib activity:

```json
{
  "status": "away",
  "since": "2026-03-13T06:45:00.000000Z",
  "is_in_crib": false
}
```

> **Tip:** Check for `null` values and empty `sessions` arrays before processing. Don't assume every day has data.

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

### Python: Daily Sleep Summary

```python
import requests

TOKEN = "cw_your_token_here"
BASE = "https://integrations.cradlewise.com/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Fetch today's key metrics
resp = requests.get(
    f"{BASE}/sleep/day-metrics",
    headers=HEADERS,
    params={
        "start_time": "2026-03-12 00:00:00",
        "end_time": "2026-03-13 00:00:00",
    },
)
data = resp.json()

for day in data["metrics"]:
    print(f"Date: {day['date'][:10]}")
    for banner in day["banners"]:
        val = banner["data"]["display_value"] or "—"
        print(f"  {banner['header']}: {val}")
```

### Python: Home Automation Status Poller

```python
import requests
import time

TOKEN = "cw_your_token_here"
URL = "https://integrations.cradlewise.com/api/v1/baby/status"
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
const BASE = "https://integrations.cradlewise.com/api/v1";

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
  - resource: https://integrations.cradlewise.com/api/v1/baby/status
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
  https://integrations.cradlewise.com/api/v1/baby/status

# Day metrics for a specific day
curl -H "Authorization: Bearer $TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/day-metrics?start_time=2026-03-12%2000:00:00&end_time=2026-03-13%2000:00:00"

# Sleep sessions (c-chart) for last 24 hours
curl -H "Authorization: Bearer $TOKEN" \
  "https://integrations.cradlewise.com/api/v1/sleep/c-chart?start_time=2026-03-12%2000:00:00&end_time=2026-03-13%2000:00:00"
```

---

## Detailed Endpoint Documentation

Each stable endpoint has a comprehensive deep-dive doc with full response schemas, edge cases, practical code examples, and gotchas discovered through testing.

**Stable endpoints:**

| Endpoint | Doc |
|----------|-----|
| Baby Status | [docs/baby-status.md](docs/baby-status.md) |
| Sleep Sessions (C-Chart) | [docs/c-chart.md](docs/c-chart.md) |
| Day Metrics | [docs/day-metrics.md](docs/day-metrics.md) |

**Planned endpoints** (schemas are drafts — may change before release):

| Endpoint | Doc |
|----------|-----|
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

## Roadmap

These endpoints are planned but **not yet available**. Requests will return `404`. We're sharing the planned schemas so you can see what's coming and plan your integrations accordingly.

| Endpoint | Description | Planned Schema |
|----------|-------------|----------------|
| `/api/v1/sleep/weekly-sleep-graph` | Daily sleep totals for a week (day vs. night) | [docs/weekly-sleep-graph.md](docs/weekly-sleep-graph.md) |
| `/api/v1/sleep/weekly-rise-and-bed-time` | Rise/bed times for the week | [docs/weekly-rise-and-bed-time.md](docs/weekly-rise-and-bed-time.md) |
| `/api/v1/sleep/weekly-nap-planner` | Nap duration and wake window trends | [docs/weekly-nap-planner.md](docs/weekly-nap-planner.md) |
| `/api/v1/sleep/weekly-sleep-metrics` | All weekly metrics in one response | [docs/weekly-sleep-metrics.md](docs/weekly-sleep-metrics.md) |
| `/api/v1/sleep/weekly-longest-stretch` | Longest sleep stretch per day (week) | [docs/weekly-longest-stretch.md](docs/weekly-longest-stretch.md) |
| `/api/v1/sleep/monthly-sleep-graph` | Monthly sleep totals | [docs/monthly-sleep-graph.md](docs/monthly-sleep-graph.md) |
| `/api/v1/sleep/monthly-rise-and-bed-time` | Rise/bed times (monthly) | [docs/monthly-rise-and-bed-time.md](docs/monthly-rise-and-bed-time.md) |
| `/api/v1/sleep/monthly-longest-stretch` | Longest stretch (monthly) | [docs/monthly-longest-stretch.md](docs/monthly-longest-stretch.md) |
| `/api/v1/sleep/monthly-sleep-metrics` | All monthly metrics in one response | [docs/monthly-sleep-metrics.md](docs/monthly-sleep-metrics.md) |

Also on the roadmap:
- **Webhooks / push notifications** — real-time status change events (no polling required)
- **Self-service token generation** from [mycrib.cradlewise.com](https://mycrib.cradlewise.com)
- **MCP server** for native AI tool integration
- **`/baby/profile` endpoint** — baby's day start time, timezone, and crib config (currently only visible in the app)

---

## Versioning

The current API version is `v1`, reflected in the base URL (`/api/v1/`).

- **Stable endpoints** have a locked schema. We will not make breaking changes to stable endpoints within `v1`.
- **When `v2` ships**, `v1` will continue to work for a minimum of 6 months with a deprecation notice. We'll announce version changes via email to all beta testers and in the Changelog below.
- **Non-breaking additions** (new fields in responses, new endpoints) may be added to `v1` at any time. Your code should ignore unknown fields gracefully.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-17 | Moved planned endpoints to Roadmap section; fixed day-metrics banner documentation to match actual API response; added No Data Responses section; added Versioning guidance |
| 2026-03-14 | Initial public beta release — stable endpoints: baby/status, c-chart, day-metrics |

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

**What about the weekly/monthly endpoints?**
They're on the [Roadmap](#roadmap) but not yet live. Requests will return `404`. The planned schemas are documented so you can see what's coming. Only the three stable endpoints (baby/status, c-chart, day-metrics) are available today.

**Is there an SLA or uptime guarantee?**
No. This API is provided as-is, without guarantees around uptime, latency, or data accuracy. It runs on the same infrastructure as our internal tools, but is not monitored to production standards.

---

## Endpoint Quick Reference

**Available now:**

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/baby/status` | — | Real-time baby status |
| GET | `/api/v1/sleep/c-chart` | `start_time`, `end_time` | Individual sleep sessions |
| GET | `/api/v1/sleep/day-metrics` | `start_time`, `end_time` | Daily key metrics |

**Planned** (see [Roadmap](#roadmap) for details — these are not yet live):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sleep/weekly-sleep-graph` | Daily sleep totals (week) |
| GET | `/api/v1/sleep/weekly-rise-and-bed-time` | Rise/bed times (week) |
| GET | `/api/v1/sleep/weekly-nap-planner` | Nap/wake windows (week) |
| GET | `/api/v1/sleep/weekly-sleep-metrics` | All weekly metrics combined |
| GET | `/api/v1/sleep/weekly-longest-stretch` | Longest sleep stretch (week) |
| GET | `/api/v1/sleep/monthly-sleep-graph` | Monthly sleep totals |
| GET | `/api/v1/sleep/monthly-rise-and-bed-time` | Rise/bed times (monthly) |
| GET | `/api/v1/sleep/monthly-longest-stretch` | Longest stretch (monthly) |
| GET | `/api/v1/sleep/monthly-sleep-metrics` | All monthly metrics combined |

---

*Built by Cradlewise for tinkerers and developers. First baby monitor company with a public API.*
