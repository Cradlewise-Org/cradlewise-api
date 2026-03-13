# Day Metrics

Key daily sleep metrics for one or more days — rise time, bed time, nap count, longest stretch, time in bed, awake time, and soothe count. This is the best endpoint for a daily summary card or pediatrician-friendly report.

## Request

```
GET /api/v1/sleep/day-metrics
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
  "https://api.cradlewise.com/api/v1/sleep/day-metrics?start_time=2026-03-10%2000:00:00&end_time=2026-03-11%2000:00:00"
```

---

## Response

### Single-Day Example

```json
{
  "header": "KEY METRICS",
  "timezone": "Asia/Kolkata",
  "metrics": [
    {
      "date": "2026-03-10 00:00:00.000000",
      "banners": [
        {
          "type": "soothes",
          "header": "SOOTHES",
          "data": {
            "value": null,
            "display_value": "",
            "description": "no of soothes"
          },
          "subtext": "",
          "subtext_header": "WHAT IS A SOOTHE?"
        },
        {
          "type": "info",
          "header": "RISE TIME",
          "data": {
            "value": "2026-03-10 03:48:34.314255",
            "display_value": "9:18 am",
            "description": "rise time"
          }
        },
        {
          "type": "info",
          "header": "BED TIME",
          "data": {
            "value": "2026-03-10 03:49:44.908840",
            "display_value": "9:19 am",
            "description": "bed time"
          }
        },
        {
          "type": "naps",
          "header": "NAPS",
          "data": {
            "value": 0,
            "display_value": "0",
            "naps": [],
            "description": "no of naps"
          }
        },
        {
          "type": "info",
          "header": "LONGEST STRETCH",
          "data": {
            "value": 72615.09,
            "display_value": "20h 10m",
            "description": "longest stretch of undisturbed sleep"
          },
          "subtext": "9:19 am - 5:30 am"
        },
        {
          "type": "info",
          "header": "TIME IN BED",
          "data": {
            "value": 1210.25,
            "display_value": "20h 10m",
            "description": "total time spend in crib including sleep and awake sessions"
          }
        },
        {
          "type": "info",
          "header": "AWAKE IN BED",
          "data": {
            "value": null,
            "display_value": "",
            "description": "total awake time spend in crib"
          }
        }
      ]
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `header` | string | Always `"KEY METRICS"` |
| `timezone` | string | Baby's configured timezone |
| `metrics` | array | One entry per day in the requested range |

### Metric Object (per day)

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | The date this metric covers (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `banners` | array | Array of metric cards (always 7 items, in fixed order) |

### Banner Object

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | `"info"`, `"soothes"`, or `"naps"` |
| `header` | string | Metric name (see table below) |
| `image` | string | Always empty string |
| `data` | object | The metric value (see below) |
| `subtext` | string or null | Additional context (e.g., time range for longest stretch) |
| `subtext_header` | string or null | Header for the subtext |

### Banner Types (in order)

| # | Header | `data.value` | `data.display_value` | Notes |
|---|--------|-------------|---------------------|-------|
| 1 | SOOTHES | null or number | Count or empty | Number of crib soothing activations |
| 2 | RISE TIME | timestamp string | e.g., `"9:18 am"` | When baby woke up for the day |
| 3 | BED TIME | timestamp string | e.g., `"9:19 am"` | When baby went to bed |
| 4 | NAPS | number | Count string | `data.naps` array has individual nap details |
| 5 | LONGEST STRETCH | seconds (number) | e.g., `"20h 10m"` | `subtext` shows the time range |
| 6 | TIME IN BED | minutes (number) | e.g., `"20h 10m"` | Total crib time including awake |
| 7 | AWAKE IN BED | seconds or null | Duration or empty | Time spent awake while in crib |

### Data Object

| Field | Type | Description |
|-------|------|-------------|
| `value` | varies | Raw value — `null` when no data, number for durations/counts, string for timestamps |
| `display_value` | string | Human-readable formatted value. Empty string when no data |
| `description` | string | What this metric measures |
| `naps` | array | (NAPS banner only) Individual nap details |

---

## Multi-Day Queries

When the range spans multiple days, `metrics` contains one entry per day:

```bash
# 3-day range
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/day-metrics?start_time=2026-03-08%2000:00:00&end_time=2026-03-11%2000:00:00"
```

```python
# Each day's metrics
for day in data["metrics"]:
    date = day["date"][:10]
    banners = {b["header"]: b["data"] for b in day["banners"]}
    rise = banners["RISE TIME"]["display_value"] or "—"
    bed = banners["BED TIME"]["display_value"] or "—"
    longest = banners["LONGEST STRETCH"]["display_value"] or "—"
    naps = banners["NAPS"]["display_value"]
    print(f"{date}: Rise {rise}, Bed {bed}, Longest {longest}, Naps {naps}")
```

Example output:
```
2026-03-08: Rise —, Bed —, Longest 24h, Naps 0
2026-03-09: Rise —, Bed 4:17 pm, Longest 17h 1m, Naps 1
2026-03-10: Rise 9:18 am, Bed 9:19 am, Longest 20h 10m, Naps 0
```

---

## Null Values

When no data exists for a metric (e.g., baby wasn't in the crib):
- `value`: `null`
- `display_value`: `""` (empty string)

This happens for rise time, bed time, and awake time when the baby was out of the crib all day. Check for empty `display_value` before rendering.

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Per hour | 60 requests |
| Daily cap (shared with all endpoints) | 500 requests |

---

## Edge Cases

### Future Dates

Returns a metrics entry with all banners having `null` values and empty `display_value`. No error — just empty data.

### Reversed Date Range (`start_time` > `end_time`)

Returns `500 Internal Server Error`. Unlike C-Chart (which returns empty results), Day Metrics crashes on reversed ranges. **Always validate your inputs.**

### Naps Array

The NAPS banner includes a `naps` sub-array with individual nap details. When there are no naps, this is an empty array `[]`.

### Rise Time and Bed Time

These are in the baby's local timezone (per the `timezone` field), not UTC. The `value` field contains the raw UTC timestamp, while `display_value` shows the localized, human-readable time.

### Time in Bed Units

The `value` for TIME IN BED is in **minutes**, while LONGEST STRETCH and AWAKE IN BED use **seconds**. Always use `display_value` for display, or check the `description` field for unit clarity.

---

## Error Responses

| Status | Cause | Response |
|--------|-------|----------|
| 401 | Missing or invalid token | `{"detail": "Invalid token"}` |
| 403 | No Nurture Plus subscription | `{"detail": "Nurture Plus subscription required"}` |
| 422 | Missing required parameters | `{"detail": [{"msg": "Field required", ...}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded"}` |
| 500 | Invalid date format or reversed range | `Internal Server Error` |
