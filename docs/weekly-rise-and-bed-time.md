# Weekly Rise and Bed Time `Beta`

> **Beta:** This endpoint is functional but still being refined. Response schema or data accuracy may change without notice.

Weekly averages and daily plot data for rise time and bed time. Best for trend charts — shows how the baby's wake-up and sleep-onset times shift across a week.

## Request

```
GET /api/v1/sleep/weekly-rise-and-bed-time
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
  "https://api.cradlewise.com/api/v1/sleep/weekly-rise-and-bed-time?start_time=2026-03-06%2000:00:00&end_time=2026-03-13%2000:00:00"
```

---

## Response

### 7-Day Example

```json
{
  "day_start_time": "2026-03-06 02:30:00.000000",
  "avg_rise_time": "10:43 am",
  "avg_bed_time": "--",
  "plot_values": [
    {
      "rise_time": "",
      "bed_time": "",
      "date": "2026-03-06 02:30:00.000000"
    },
    {
      "rise_time": "",
      "bed_time": "",
      "date": "2026-03-07 02:30:00.000000"
    },
    {
      "rise_time": "",
      "bed_time": "",
      "date": "2026-03-08 02:30:00.000000"
    },
    {
      "rise_time": "2026-03-09 10:43:15.404243",
      "bed_time": "",
      "date": "2026-03-09 02:30:00.000000"
    },
    {
      "rise_time": "",
      "bed_time": "",
      "date": "2026-03-10 02:30:00.000000"
    },
    {
      "rise_time": "",
      "bed_time": "",
      "date": "2026-03-11 02:30:00.000000"
    },
    {
      "rise_time": "",
      "bed_time": "",
      "date": "2026-03-12 02:30:00.000000"
    }
  ]
}
```

---

## Fields

### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| `day_start_time` | string | The baby's configured day boundary — the hour at which a "day" begins (`YYYY-MM-DD HH:MM:SS.ffffff`, UTC) |
| `avg_rise_time` | string | Average rise time across the week, human-readable (e.g., `"10:43 am"`). `"--"` when insufficient data |
| `avg_bed_time` | string | Average bed time across the week, human-readable (e.g., `"8:15 pm"`). `"--"` when insufficient data |
| `plot_values` | array | One entry per day in the requested range |

### Plot Value Object (per day)

| Field | Type | Description |
|-------|------|-------------|
| `rise_time` | string | UTC timestamp when the baby woke up for the day (`YYYY-MM-DD HH:MM:SS.ffffff`). Empty string `""` when no data |
| `bed_time` | string | UTC timestamp when the baby went to bed (`YYYY-MM-DD HH:MM:SS.ffffff`). Empty string `""` when no data |
| `date` | string | The day this entry covers, offset by `day_start_time` — not midnight (`YYYY-MM-DD HH:MM:SS.ffffff`) |

---

## Practical Usage (Python)

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
params = {
    "start_time": "2026-03-06 00:00:00",
    "end_time": "2026-03-13 00:00:00"
}

resp = requests.get(
    "https://api.cradlewise.com/api/v1/sleep/weekly-rise-and-bed-time",
    headers=headers,
    params=params
)
data = resp.json()

print(f"Avg Rise: {data['avg_rise_time']}")
print(f"Avg Bed:  {data['avg_bed_time']}")

for day in data["plot_values"]:
    date = day["date"][:10]
    rise = day["rise_time"][11:19] if day["rise_time"] else "—"
    bed = day["bed_time"][11:19] if day["bed_time"] else "—"
    print(f"{date}: Rise {rise}, Bed {bed}")
```

Example output:
```
Avg Rise: 10:43 am
Avg Bed:  --
2026-03-06: Rise —, Bed —
2026-03-07: Rise —, Bed —
2026-03-08: Rise —, Bed —
2026-03-09: Rise 10:43:15, Bed —
2026-03-10: Rise —, Bed —
2026-03-11: Rise —, Bed —
2026-03-12: Rise —, Bed —
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Per hour | 60 requests |
| Daily cap (shared with all endpoints) | 500 requests |

---

## Edge Cases

### Empty Strings for Missing Days

Days where no rise or bed event was recorded return empty strings (`""`), not `null`. Always check for empty string before parsing timestamps:

```python
if day["rise_time"]:
    # parse timestamp
else:
    # no data for this day
```

### `"--"` Averages

When there aren't enough data points to compute a meaningful average, `avg_rise_time` and `avg_bed_time` return the literal string `"--"` instead of a time. Check for this before displaying:

```python
if data["avg_rise_time"] != "--":
    print(data["avg_rise_time"])
```

### `day_start_time` Offset

The `date` field in each plot value is offset by the baby's configured day boundary, not midnight. For example, a family with a `day_start_time` of `02:30` (UTC) means each "day" starts at 2:30 AM UTC. The `date` values in `plot_values` will be `YYYY-MM-DD 02:30:00.000000`, not `YYYY-MM-DD 00:00:00.000000`. Use the date portion (`[:10]`) for display; don't assume midnight alignment.

### Rise and Bed Timestamps Are UTC

The `rise_time` and `bed_time` values in `plot_values` are raw UTC timestamps. Convert to the baby's local timezone for display. The endpoint does not include a `timezone` field — use the timezone from the Day Metrics or Baby Status endpoint.

### Partial Weeks

If the range covers fewer than 7 days, `plot_values` will contain only as many entries as days in the range. The averages still compute over whatever data is present.

---

## Error Responses

| Status | Cause | Response |
|--------|-------|----------|
| 401 | Missing or invalid token | `{"detail": "Invalid token"}` |
| 403 | No Nurture Plus subscription | `{"detail": "Nurture Plus subscription required"}` |
| 422 | Missing required parameters | `{"detail": [{"msg": "Field required", ...}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded"}` |
| 500 | Invalid date format or `T` separator | `Internal Server Error` |
