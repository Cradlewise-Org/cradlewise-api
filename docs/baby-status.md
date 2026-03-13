# Baby Status

Real-time status of your baby in the Cradlewise crib. This is the primary endpoint for home automation — poll it to trigger actions based on whether your baby is sleeping, awake, crying, or out of the crib.

## Request

```
GET /api/v1/baby/status
```

No query parameters. The baby is identified from your token.

### curl

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.cradlewise.com/api/v1/baby/status
```

---

## Response

### Sleeping

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

### Awake (in crib)

```json
{
  "status": "awake",
  "since": "2026-03-13T06:45:12.000000Z",
  "is_in_crib": true,
  "crib_mode": {
    "bounce": "off",
    "music": "off"
  },
  "timestamp": "2026-03-13T06:46:00Z"
}
```

### Away (not in crib)

```json
{
  "status": "away",
  "since": "2026-03-13T14:52:14.839627Z",
  "is_in_crib": false,
  "crib_mode": {
    "bounce": "off",
    "music": "off"
  },
  "timestamp": "2026-03-13T08:33:04Z"
}
```

### Crying

```json
{
  "status": "crying",
  "since": "2026-03-13T02:10:45.000000Z",
  "is_in_crib": true,
  "crib_mode": {
    "bounce": "on",
    "music": "on"
  },
  "timestamp": "2026-03-13T02:11:00Z"
}
```

---

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | One of: `sleeping`, `awake`, `crying`, `away`, `unknown` |
| `since` | string | ISO 8601 UTC timestamp — when the baby entered the current status |
| `is_in_crib` | boolean | `true` for all statuses except `away` |
| `crib_mode.bounce` | string | Current bounce mode (e.g., `on`, `off`, or a specific level) |
| `crib_mode.music` | string | Current sound/music mode (e.g., `on`, `off`) |
| `timestamp` | string | ISO 8601 UTC timestamp — when the server generated this response |

### Status Values

| Status | Meaning | `is_in_crib` |
|--------|---------|--------------|
| `sleeping` | Baby is asleep in the crib | `true` |
| `awake` | Baby is awake but still in the crib | `true` |
| `crying` | Baby is crying in the crib | `true` |
| `away` | Baby has been taken out of the crib | `false` |
| `unknown` | No recent recognized event (crib may be offline or transitioning) | `true` |

### `since` vs `timestamp`

These two fields serve different purposes:

- **`since`** is the time the baby entered the current status. It does **not** change between requests unless the status itself changes. Use this to know how long the baby has been in the current state.
- **`timestamp`** is the server time when the response was generated. It changes on every request. Use this to verify your polling is working.

**Example:** If you poll every 30 seconds and the baby is sleeping, `since` will stay the same across all responses while `timestamp` advances by ~30s each time. When the baby wakes up, `since` will jump to the new wake time.

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Per minute | 2 requests |
| Daily cap (shared with all endpoints) | 500 requests |

This supports polling every 30 seconds. If you poll more frequently, you'll receive a `429` response.

### Rate Limit Response

```
HTTP/1.1 429 Too Many Requests
x-ratelimit-remaining: 0
x-ratelimit-reset: 1710288000
```

```json
{
  "detail": "Rate limit exceeded"
}
```

`x-ratelimit-reset` is a Unix timestamp. Wait until that time before retrying.

### Recommended Polling Strategy

Poll every 30 seconds during the hours your automations are active, not 24/7. For example, polling from 6 PM to 8 AM (14 hours) uses ~1,680 requests/day — over the 500/day cap. Options:

- **Poll during sleep hours only** (8 PM to 7 AM = 11 hours = ~1,320 requests). Still over cap.
- **Poll every 60 seconds** during active hours. 14 hours = 840 requests — closer but still high.
- **Best approach:** Poll every 60 seconds during a focused window (e.g., 7 PM to 7 AM) = ~720 requests. Or use conditional logic to stop polling after a status change you've already handled.

The 2/minute limit is the binding constraint for most users, not the daily cap.

---

## Error Responses

### 401 — Missing or Invalid Token

**No `Authorization` header:**
```bash
curl https://api.cradlewise.com/api/v1/baby/status
```
```json
{"detail": "Missing authorization header"}
```

**Malformed header (missing `Bearer` prefix):**
```bash
curl -H "Authorization: cw_your_token" https://api.cradlewise.com/api/v1/baby/status
```
```json
{"detail": "Missing authorization header"}
```

**Invalid or revoked token:**
```bash
curl -H "Authorization: Bearer cw_invalid_or_revoked_token" \
  https://api.cradlewise.com/api/v1/baby/status
```
```json
{"detail": "Invalid token"}
```

**Expired token (past 1-year validity):**
```json
{"detail": "Token expired"}
```

### 403 — Subscription Required

Token is valid but the baby's Nurture Plus subscription is not active:
```json
{"detail": "Nurture Plus subscription required"}
```

This happens if your subscription lapses. Your token is not deleted — reactivating the subscription restores access immediately.

### 404 — No Data

No sleep events recorded for this baby (new crib, never used):
```json
{"detail": "No status data found for this baby"}
```

### 405 — Wrong HTTP Method

Only `GET` is supported:
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.cradlewise.com/api/v1/baby/status
```
```json
{"detail": "Method Not Allowed"}
```

### 429 — Rate Limited

More than 2 requests in a 1-minute window:
```json
{"detail": "Rate limit exceeded"}
```

---

## Edge Cases

### Baby status hasn't changed in a long time

If the crib hasn't reported a new event (e.g., it's powered off or in storage), the last known status is returned. The `since` field may be days or weeks old. Check the `since` timestamp to determine freshness.

### `unknown` status

This appears when the most recent event from the crib doesn't map to a recognized state (e.g., a firmware-level event that isn't sleep/wake/cry/away). It's uncommon — treat it as "status not determined" and wait for the next poll.

### `crib_mode` when baby is away

When `status` is `away`, `crib_mode` reflects the last known device state (usually both `off`). The crib doesn't actively bounce or play music when the baby isn't in it.

### Security

- The token can only read data for the baby it was generated for. There is no way to access another baby's data.
- SQL injection and other malicious inputs in the `Authorization` header are safely rejected as `401 Invalid token`.
- Oversized tokens (tested up to 10,000 characters) are rejected without crashing.
- No PII is returned — no parent name, email, or address appears in any response.

---

## Home Automation Examples

### Trigger on status change (Python)

```python
import requests, time

TOKEN = "cw_your_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
URL = "https://api.cradlewise.com/api/v1/baby/status"

last = None
while True:
    r = requests.get(URL, headers=HEADERS)
    if r.status_code == 429:
        time.sleep(60)
        continue
    if r.ok:
        s = r.json()["status"]
        if s != last:
            print(f"Changed: {last} -> {s}")
            # Your automation here
            last = s
    time.sleep(30)
```

### Home Assistant REST sensor

```yaml
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
```

### Automation ideas

| Trigger | Action |
|---------|--------|
| `status` changes to `sleeping` | Mute doorbell, dim hallway lights, set thermostat to sleep mode |
| `status` changes to `awake` | Turn on nursery nightlight (low brightness), start bottle warmer |
| `status` changes to `crying` | Send push notification, announce on smart speakers |
| `status` changes to `away` | Turn off nursery devices, resume normal home lighting |
