# Monthly Sleep Metrics `Beta`

> **Beta:** This endpoint is functional but still being refined. Response schema or data accuracy may change without notice.

Composite endpoint that combines sleep graph, rise/bed time, longest stretch, and nap data into a single response — indexed by your baby's age in months. This is the most convenient endpoint for building a monthly overview dashboard in one API call.

## Request

```
GET /api/v1/sleep/monthly-sleep-metrics
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
  "https://api.cradlewise.com/api/v1/sleep/monthly-sleep-metrics?start_time=2025-11-01%2000:00:00&end_time=2026-01-01%2000:00:00"
```

Note: URL-encode the space as `%20`.

---

## Response

### Multi-Month Example

```json
{
  "sleep_graph_metrics": {
    "plot_values": [
      {
        "month": "0M",
        "avg_sleep_in_mins": 1387.0,
        "avg_day_sleep_in_mins": 126.0,
        "avg_night_sleep_in_mins": 1261.0
      },
      {
        "month": "1M",
        "avg_sleep_in_mins": 1362.0,
        "avg_day_sleep_in_mins": 24.0,
        "avg_night_sleep_in_mins": 1338.0
      }
    ]
  },
  "rise_and_bed_time_metrics": {
    "plot_values": [
      {
        "month": "0M",
        "avg_rise_time": "2025-11-29 23:55:30.000000",
        "avg_rise_time_display_text": "05:25 am",
        "avg_bed_time": "2025-11-30 03:07:10.000000",
        "avg_bed_time_display_text": "08:37 am"
      }
    ]
  },
  "longest_stretch_metrics": {
    "plot_values": [
      {
        "month": "0M",
        "longest_stretch_in_mins": 1270.0,
        "longest_stretch_in_hours": 21.2,
        "longest_stretch_display_text": "21h 10m"
      }
    ]
  },
  "avg_no_of_naps_metrics": {
    "plot_values": []
  }
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `sleep_graph_metrics` | object | Monthly averages for total, day, and night sleep duration |
| `rise_and_bed_time_metrics` | object | Monthly average rise and bed times with display-friendly strings |
| `longest_stretch_metrics` | object | Monthly longest uninterrupted sleep stretch |
| `avg_no_of_naps_metrics` | object | Monthly average number of naps. May have empty `plot_values` |

Each top-level object contains a single `plot_values` array of monthly data points.

### Month Labeling

**This endpoint is unique** — the `month` field uses relative age labels like `"0M"`, `"1M"`, `"2M"`, representing the baby's age in months since birth, **not** calendar months. This is different from every other sleep endpoint, which uses calendar dates.

| `month` | Meaning |
|---------|---------|
| `"0M"` | Baby's first month of life (birth to 1 month) |
| `"1M"` | Baby's second month of life (1 to 2 months) |
| `"2M"` | Baby's third month of life (2 to 3 months) |

The API determines these labels from the baby's birth date in their profile. You do not control which months appear — the query window determines which age-months have data.

### Sleep Graph Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `month` | string | Baby's age in months (`"0M"`, `"1M"`, etc.) |
| `avg_sleep_in_mins` | number | Average total sleep per day that month (minutes) |
| `avg_day_sleep_in_mins` | number | Average daytime sleep per day that month (minutes) |
| `avg_night_sleep_in_mins` | number | Average nighttime sleep per day that month (minutes) |

`avg_sleep_in_mins` = `avg_day_sleep_in_mins` + `avg_night_sleep_in_mins`.

### Rise and Bed Time Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `month` | string | Baby's age in months (`"0M"`, `"1M"`, etc.) |
| `avg_rise_time` | string | Average wake-up time as a raw timestamp (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `avg_rise_time_display_text` | string | Human-readable rise time (e.g., `"05:25 am"`) |
| `avg_bed_time` | string | Average bedtime as a raw timestamp (`YYYY-MM-DD HH:MM:SS.ffffff`) |
| `avg_bed_time_display_text` | string | Human-readable bed time (e.g., `"08:37 am"`) |

**Note:** The raw timestamp fields (`avg_rise_time`, `avg_bed_time`) use an arbitrary reference date — only the time-of-day component is meaningful. Use the `_display_text` fields for rendering.

### Longest Stretch Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `month` | string | Baby's age in months (`"0M"`, `"1M"`, etc.) |
| `longest_stretch_in_mins` | number | Longest uninterrupted sleep stretch that month (minutes) |
| `longest_stretch_in_hours` | number | Same value converted to hours (1 decimal place) |
| `longest_stretch_display_text` | string | Human-readable duration (e.g., `"21h 10m"`) |

### Average Number of Naps Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `month` | string | Baby's age in months (`"0M"`, `"1M"`, etc.) |

This sub-object follows the same `plot_values` pattern but may frequently return an empty array, especially for very young babies or when nap detection has insufficient data.

---

## Date Format

**Use space-separated format only:**

| Format | Works? |
|--------|--------|
| `2026-03-10 00:00:00` | Yes |
| `2026-03-10%2000:00:00` | Yes (URL-encoded space) |
| `2026-03-10T00:00:00` | **No** — returns `500 Internal Server Error` |

This applies to all sleep endpoints, not just Monthly Sleep Metrics.

---

## Practical Usage

### Querying All Available Months

Use a wide date range to capture all months since birth:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-sleep-metrics?start_time=2025-09-01%2000:00:00&end_time=2026-03-13%2000:00:00"
```

The API returns only months that have data — it won't pad missing months with zeros.

### Querying a Single Month

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.cradlewise.com/api/v1/sleep/monthly-sleep-metrics?start_time=2025-11-01%2000:00:00&end_time=2025-12-01%2000:00:00"
```

Returns a single entry in each `plot_values` array (if data exists for that period).

### Building a Monthly Sleep Trend (Python)

```python
import requests

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.cradlewise.com/api/v1"

resp = requests.get(f"{BASE}/sleep/monthly-sleep-metrics", headers=HEADERS, params={
    "start_time": "2025-09-01 00:00:00",
    "end_time": "2026-03-13 00:00:00",
})
data = resp.json()

# Sleep duration trend
print("Monthly Sleep Averages:")
for point in data["sleep_graph_metrics"]["plot_values"]:
    total_hrs = point["avg_sleep_in_mins"] / 60
    day_hrs = point["avg_day_sleep_in_mins"] / 60
    night_hrs = point["avg_night_sleep_in_mins"] / 60
    print(f"  {point['month']}: {total_hrs:.1f}h total (day: {day_hrs:.1f}h, night: {night_hrs:.1f}h)")

# Rise and bed times
print("\nRise & Bed Times:")
for point in data["rise_and_bed_time_metrics"]["plot_values"]:
    print(f"  {point['month']}: rise {point['avg_rise_time_display_text']}, "
          f"bed {point['avg_bed_time_display_text']}")

# Longest stretch
print("\nLongest Stretch:")
for point in data["longest_stretch_metrics"]["plot_values"]:
    print(f"  {point['month']}: {point['longest_stretch_display_text']} "
          f"({point['longest_stretch_in_hours']}h)")

# Naps (may be empty)
naps = data["avg_no_of_naps_metrics"]["plot_values"]
if naps:
    print("\nAverage Naps:")
    for point in naps:
        print(f"  {point['month']}: {point}")
else:
    print("\nNo nap data available")
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

### Month Labels Are Baby Age, Not Calendar Months

The `"0M"`, `"1M"` labels represent the baby's age in months since birth. If your baby was born in October 2025, `"0M"` is October, `"1M"` is November, etc. You cannot control or predict these labels from the query parameters alone — they depend on the baby's birth date stored in the profile.

### Mismatched plot_values Lengths

Each of the four sub-objects may return a different number of entries in `plot_values`. For example, `sleep_graph_metrics` might have data for months `"0M"` and `"1M"`, while `rise_and_bed_time_metrics` only has `"0M"`. Do not assume all four arrays are the same length.

### Empty plot_values

Any sub-object may return an empty `plot_values` array. This is especially common for `avg_no_of_naps_metrics`, which may have no data for young babies or periods with insufficient nap detection.

### Raw Timestamps in Rise/Bed Time

The `avg_rise_time` and `avg_bed_time` fields contain full timestamps with an arbitrary reference date. Only the time component is meaningful. Always prefer the `_display_text` fields for rendering. The raw timestamps exist for programmatic time-of-day comparisons.

### Query Window vs. Returned Months

The query window determines which age-months are included, but the `month` labels reflect the baby's age — not the dates you queried. A wide query returns more months; a narrow query returns fewer. If the window falls entirely outside any period with data, all `plot_values` arrays will be empty.

### Reversed Date Range (`start_time` > `end_time`)

Returns `200 OK` with empty `plot_values` arrays across all four sub-objects. **No error is raised.** Always validate that `start_time < end_time` in your code.

### Large Date Ranges

Querying a full year returns at most 12 monthly data points per sub-object — the response is always small regardless of the date range, since data is aggregated by month.

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
