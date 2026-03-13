"""
Cradlewise API — Baby Status Poller

Polls your baby's status every 30 seconds and prints changes.
Use this as a starting point for home automation triggers.

Usage:
    export CRADLEWISE_TOKEN="cw_your_token_here"
    python status_poller.py
"""

import os
import sys
import time
import requests

TOKEN = os.environ.get("CRADLEWISE_TOKEN")
if not TOKEN:
    print("Set CRADLEWISE_TOKEN environment variable")
    sys.exit(1)

BASE_URL = "https://api.cradlewise.com/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
POLL_INTERVAL = 30  # seconds


def get_status():
    resp = requests.get(f"{BASE_URL}/baby/status", headers=HEADERS)

    if resp.status_code == 429:
        reset = int(resp.headers.get("X-RateLimit-Reset", 0))
        wait = max(reset - int(time.time()), 30)
        print(f"Rate limited. Waiting {wait}s...")
        time.sleep(wait)
        return None

    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.json().get('detail', 'Unknown error')}")
        return None

    return resp.json()


def on_status_change(old_status, new_status, data):
    """Called when baby status changes. Customize this for your automations."""
    print(f"[{data['timestamp']}] Status: {old_status} -> {new_status}")

    if new_status == "sleeping":
        print("  -> Baby is sleeping. Mute doorbell, dim lights.")
    elif new_status == "awake":
        print("  -> Baby is awake. Turn on nightlight, start bottle warmer.")
    elif new_status == "crying":
        print("  -> Baby is crying. Send notification.")
    elif new_status == "away":
        print("  -> Baby removed from crib.")


def main():
    print(f"Polling baby status every {POLL_INTERVAL}s...")
    print("Press Ctrl+C to stop.\n")

    last_status = None

    while True:
        data = get_status()
        if data:
            status = data["status"]
            if status != last_status:
                on_status_change(last_status, status, data)
                last_status = status

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
