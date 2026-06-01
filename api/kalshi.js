// Vercel serverless proxy: Kalshi public markets list.
// CORS-restricted from the browser, fine from a server. Supports cursor
// paging so the frontend can sweep multiple pages.
//
// Frontend calls: /api/kalshi?status=open&limit=1000&cursor=<c>

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();

  const params = new URLSearchParams();
  params.set('status', String(req.query.status || 'open'));
  params.set('limit', String(req.query.limit || '1000'));
  if (req.query.cursor) params.set('cursor', String(req.query.cursor));

  try {
    const upstream = await fetch(
      `https://api.elections.kalshi.com/trade-api/v2/markets?${params}`,
      { headers: { Accept: 'application/json' } },
    );
    const body = await upstream.text();
    res.setHeader('Cache-Control', 'public, max-age=60'); // 1-minute cache
    res.setHeader('Content-Type', 'application/json');
    return res.status(upstream.status).send(body);
  } catch (e) {
    return res.status(502).json({ error: 'upstream_failed', message: String(e && e.message || e) });
  }
}
