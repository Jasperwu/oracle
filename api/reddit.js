// Vercel serverless proxy: Reddit public search.
// Reddit blocks browser-direct calls (CORS + UA filtering) and also blocks
// generic server UAs (returns 403). Use the old.reddit.com host with a
// realistic UA, and fall back to a public read-only alternative on 403.
//
// Frontend calls: /api/reddit?q=<q>&sort=relevance&t=month&limit=20

const REALISTIC_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15';

async function fetchOnce(host, params) {
  return fetch(`https://${host}/search.json?${params}`, {
    headers: {
      'User-Agent': REALISTIC_UA,
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'en-US,en;q=0.9',
    },
  });
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();

  const q = String(req.query.q || '').trim();
  if (!q) return res.status(400).json({ error: 'missing q' });

  const params = new URLSearchParams();
  params.set('q', q);
  params.set('sort', String(req.query.sort || 'relevance'));
  params.set('t', String(req.query.t || 'month'));
  params.set('limit', String(req.query.limit || '20'));
  params.set('raw_json', '1');

  try {
    // Try old.reddit.com first — historically more permissive than www
    let upstream = await fetchOnce('old.reddit.com', params);
    if (upstream.status === 403 || upstream.status === 429) {
      // Retry on www with the same realistic UA
      upstream = await fetchOnce('www.reddit.com', params);
    }
    const body = await upstream.text();
    res.setHeader('Cache-Control', 'public, max-age=300'); // 5-minute cache
    res.setHeader('Content-Type', 'application/json');
    return res.status(upstream.status).send(body);
  } catch (e) {
    return res.status(502).json({ error: 'upstream_failed', message: String(e && e.message || e) });
  }
}
