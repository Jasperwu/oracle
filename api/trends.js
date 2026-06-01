// Vercel serverless proxy: Google Trends "interest over time".
// Google Trends has no official API and is CORS-blocked from the browser. The
// unofficial flow is two hops, both returning a ")]}'," prefixed JSON body:
//   1) /api/explore        → hand back widget tokens + request payloads
//   2) /api/widgetdata/multiline → the actual TIMESERIES data for a token
// We run both server-side and return a clean { keyword, series, points }.
//
// Frontend calls: /api/trends?q=<keyword>&geo=<optional ISO geo>&time=<optional>
//
// ⚠️ Unofficial + rate-limited by Google. Treat as best-effort: any failure
// returns a 200 with series:[] so the rest of the oracle degrades gracefully.

const REALISTIC_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15';
const COMMON_HEADERS = {
  'User-Agent': REALISTIC_UA,
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'en-US,en;q=0.9',
  'Referer': 'https://trends.google.com/trends/explore',
};

// Both Trends endpoints prefix the JSON with ")]}',\n" — strip to the first {.
function parsePrefixed(text) {
  const i = text.indexOf('{');
  if (i < 0) throw new Error('unexpected trends payload');
  return JSON.parse(text.slice(i));
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();

  const q = String(req.query.q || '').trim();
  if (!q) return res.status(400).json({ error: 'missing q' });
  const geo = String(req.query.geo || '').trim();
  const time = String(req.query.time || 'today 3-m').trim();
  const hl = 'en-US', tz = '0';

  try {
    // Hop 1: explore → tokens
    const exploreReq = JSON.stringify({
      comparisonItem: [{ keyword: q, geo, time }],
      category: 0,
      property: '',
    });
    const exploreUrl = `https://trends.google.com/trends/api/explore?hl=${hl}&tz=${tz}&req=${encodeURIComponent(exploreReq)}`;
    const exRes = await fetch(exploreUrl, { headers: COMMON_HEADERS });
    if (!exRes.ok) {
      res.setHeader('Cache-Control', 'public, max-age=120');
      return res.status(200).json({ keyword: q, series: [], points: 0, note: `explore ${exRes.status}` });
    }
    const explore = parsePrefixed(await exRes.text());
    const widget = (explore.widgets || []).find((w) => w.id === 'TIMESERIES');
    if (!widget || !widget.token || !widget.request) {
      return res.status(200).json({ keyword: q, series: [], points: 0, note: 'no timeseries widget' });
    }

    // Hop 2: multiline → timeline data for that token
    const multiUrl = `https://trends.google.com/trends/api/widgetdata/multiline?hl=${hl}&tz=${tz}` +
      `&req=${encodeURIComponent(JSON.stringify(widget.request))}&token=${encodeURIComponent(widget.token)}`;
    const mlRes = await fetch(multiUrl, { headers: COMMON_HEADERS });
    if (!mlRes.ok) {
      return res.status(200).json({ keyword: q, series: [], points: 0, note: `multiline ${mlRes.status}` });
    }
    const ml = parsePrefixed(await mlRes.text());
    const timeline = (ml.default && ml.default.timelineData) || [];
    const series = timeline
      .map((d) => (Array.isArray(d.value) ? d.value[0] : null))
      .filter((v) => typeof v === 'number');

    res.setHeader('Cache-Control', 'public, max-age=1800'); // 30-min cache
    res.setHeader('Content-Type', 'application/json');
    return res.status(200).json({ keyword: q, geo, time, series, points: series.length });
  } catch (e) {
    return res.status(200).json({ keyword: q, series: [], points: 0, error: String(e && e.message || e) });
  }
}
