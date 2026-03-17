/**
 * Cradlewise API — Fetch Baby Status (Node.js)
 *
 * Usage:
 *   CRADLEWISE_TOKEN="cw_your_token_here" node fetch_status.js
 */

const TOKEN = process.env.CRADLEWISE_TOKEN;
if (!TOKEN) {
  console.error("Set CRADLEWISE_TOKEN environment variable");
  process.exit(1);
}

const BASE = "https://integrations.cradlewise.com/api/v1";

async function fetchAPI(path, params = {}) {
  const url = new URL(`${BASE}${path}`);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(`${res.status}: ${err.detail || "Unknown error"}`);
  }

  return res.json();
}

async function main() {
  // Get baby status
  const status = await fetchAPI("/baby/status");
  console.log(`Baby is ${status.status} since ${status.since}`);
  console.log(`In crib: ${status.is_in_crib}`);
  console.log(`Bounce: ${status.crib_mode.bounce}, Music: ${status.crib_mode.music}`);

  // Get today's sleep sessions
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const fmt = (d) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} 00:00:00`;

  const chart = await fetchAPI("/sleep/c-chart", {
    start_time: fmt(yesterday),
    end_time: fmt(today),
  });

  console.log(`\nSleep sessions (last 24h): ${chart.sessions.length}`);
  for (const s of chart.sessions) {
    const hrs = (s.total_time_asleep_in_seconds / 3600).toFixed(1);
    console.log(`  ${s.start_time} — ${hrs}h asleep`);
  }
}

main().catch(console.error);
