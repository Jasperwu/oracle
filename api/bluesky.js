// Vercel serverless proxy: Bluesky public post search.
// The public AppView (public.api.bsky.app) recently started rejecting some
// browser-direct calls (CORS / 403). Proxy it server-side with a realistic UA
// and re-emit with open CORS.
//
// Frontend calls: /api/bluesky?q=<q>&sort=top&limit=15

const REALISTIC_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();
  res.setHeader('Content-Type', 'application/json');

  const q = String(req.query.q || '').trim();
  if (!q) return res.status(400).json({ error: 'missing q' });

  const params = new URLSearchParams();
  params.set('q', q);
  params.set('sort', String(req.query.sort || 'top'));
  params.set('limit', String(req.query.limit || '15'));

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 8000);
  try {
    const upstream = await fetch(
      `https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?${params}`,
      { headers: { 'User-Agent': REALISTIC_UA, Accept: 'application/json' }, signal: ctrl.signal },
    );
    const text = await upstream.text();
    res.setHeader('Cache-Control', 'public, max-age=300');
    // graceful empty on any non-JSON / error so the frontend degrades cleanly
    return res.status(200).send(text.trim().startsWith('{') ? text : JSON.stringify({ posts: [] }));
  } catch (e) {
    return res.status(200).send(JSON.stringify({ posts: [] }));
  } finally {
    clearTimeout(timer);
  }
}
