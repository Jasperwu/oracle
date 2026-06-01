// Vercel serverless proxy: GDELT 2.0 DOC article search.
// Browsers get blocked by CORS when calling api.gdeltproject.org directly
// from github.io. This function fetches it server-side and re-emits with
// open CORS so the frontend can read it.
//
// Frontend calls: /api/gdelt?query=<q>&timespan=3d&maxrecords=20
// We forward exactly those params to GDELT.

export default async function handler(req, res) {
  // permissive CORS so the static frontend (any origin) can read this
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();

  const params = new URLSearchParams();
  const q = String(req.query.query || '').trim();
  if (!q) return res.status(400).json({ error: 'missing query' });
  params.set('query', q);
  params.set('mode', String(req.query.mode || 'ArtList'));
  params.set('timespan', String(req.query.timespan || '3d'));
  params.set('sort', String(req.query.sort || 'DateDesc'));
  params.set('maxrecords', String(req.query.maxrecords || '20'));
  params.set('format', 'json');

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  try {
    const target = `https://api.gdeltproject.org/api/v2/doc/doc?${params}`;
    // GDELT aggressively rate-limits shared (Vercel) IPs with 429. Retry a
    // couple of times with backoff, staying within the 10s function budget.
    let upstream, text = '';
    for (let attempt = 0; attempt < 3; attempt++) {
      upstream = await fetch(target, { headers: { Accept: 'application/json' } });
      text = await upstream.text();
      if (upstream.status !== 429) break;
      if (attempt < 2) await sleep(1500 * (attempt + 1));
    }
    res.setHeader('Cache-Control', 'public, max-age=120'); // 2-minute cache
    // GDELT sometimes returns plain text for errors; mirror its content-type
    if (text.trim().startsWith('{')) {
      res.setHeader('Content-Type', 'application/json');
    } else {
      res.setHeader('Content-Type', 'text/plain');
    }
    return res.status(upstream.status).send(text);
  } catch (e) {
    return res.status(502).json({ error: 'upstream_failed', message: String(e && e.message || e) });
  }
}
