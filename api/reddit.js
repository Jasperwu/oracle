// Vercel serverless proxy: Reddit public search.
// Reddit aggressively blocks browser-direct requests (CORS + UA filtering);
// from a server we can set a plain UA and get JSON back reliably.
//
// Frontend calls: /api/reddit?q=<q>&sort=relevance&t=month&limit=20

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

  try {
    const upstream = await fetch(`https://www.reddit.com/search.json?${params}`, {
      headers: {
        // Reddit rejects requests with no UA / browser UA — give it a plain one
        'User-Agent': 'foresight-oracle/1.0 (serverless proxy)',
        'Accept': 'application/json',
      },
    });
    const body = await upstream.text();
    res.setHeader('Cache-Control', 'public, max-age=120');
    res.setHeader('Content-Type', 'application/json');
    return res.status(upstream.status).send(body);
  } catch (e) {
    return res.status(502).json({ error: 'upstream_failed', message: String(e && e.message || e) });
  }
}
