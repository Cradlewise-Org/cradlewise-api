"""
Cradlewise API — Weekly Sleep Report

Fetches the last 7 days of sleep data and prints a summary.
Great for a daily cron job or sharing with your pediatrician.

Usage:
    export CRADLEWISE_TOKEN="cw_your_token_here"
    python weekly_report.py
"""

import os
import sys
from datetime import datetime, timedelta
import requests

TOKEN = os.environ.get("CRADLEWISE_TOKEN")
if not TOKEN:
    print("Set CRADLEWISE_TOKEN environment variable")
    sys.exit(1)

BASE_URL = "https://integrations.cradlewise.com/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def fmt_time(start_time, end_time):
    """Format start/end as YYYY-MM-DD HH:MM:SS (API format)."""
    return start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S")


def fetch(endpoint, start, end):
    s, e = fmt_time(start, end)
    resp = requests.get(
        f"{BASE_URL}/sleep/{endpoint}",
        headers=HEADERS,
        params={"start_time": s, "end_time": e},
    )
    if resp.status_code != 200:
        print(f"Error fetching {endpoint}: {resp.status_code} {resp.json().get('detail', '')}")
        return None
    return resp.json()


def main():
    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=7)

    print(f"Sleep Report: {start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}")
    print("=" * 50)

    # Weekly sleep graph
    sleep = fetch("weekly-sleep-graph", start, end)
    if sleep:
        print(f"\nAge: {sleep.get('age_banner_text', 'N/A')}")
        avg_hrs = sleep["avg_sleep_in_mins"] / 60
        print(f"Average sleep: {avg_hrs:.1f} hours/day")
        print(f"  Day sleep avg: {sleep['avg_day_sleep_in_mins'] / 60:.1f}h")
        print(f"  Night sleep avg: {sleep['avg_night_sleep_in_mins'] / 60:.1f}h")
        print("\nDaily breakdown:")
        for day in sleep["plot_values"]:
            date = day["date"][:10]
            total = day["total_sleep_in_mins"] / 60
            day_s = day["day_sleep_in_mins"] / 60
            night_s = day["night_sleep_in_mins"] / 60
            print(f"  {date}: {total:.1f}h (day: {day_s:.1f}h, night: {night_s:.1f}h)")

    # Longest stretch
    stretch = fetch("weekly-longest-stretch", start, end)
    if stretch:
        print(f"\nAvg longest stretch: {stretch['avg_longest_stretch_display_text']}")
        print("Daily longest stretch:")
        for day in stretch["plot_values"]:
            date = day["date"][:10]
            print(f"  {date}: {day['longest_stretch_display_text']}")

    # Rise and bed times
    times = fetch("weekly-rise-and-bed-time", start, end)
    if times:
        print(f"\nAvg rise time: {times.get('avg_rise_time', 'N/A')}")
        print(f"Avg bed time: {times.get('avg_bed_time', 'N/A')}")

    print("\n" + "=" * 50)
    print("Generated via Cradlewise API")


if __name__ == "__main__":
    main()
