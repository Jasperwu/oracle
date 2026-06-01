// Vercel serverless proxy: Gemini Interactions API (Deep Research Agent).
// The browser may be blocked by CORS calling generativelanguage.googleapis.com
// for the Interactions endpoints; proxy them server-side with open CORS.
//
// Frontend calls:
//   POST /api/interactions            -> create an interaction (body forwarded)
//   GET  /api/interactions?id=<id>    -> poll an interaction by id
//
// The caller's own Gemini key is passed through via the x-goog-api-key header
// (BYOK — we never store it).

const UPSTREAM = 'https://generativelanguage.googleapis.com/v1beta/interactions';
const API_REVISION = '2026-05-20';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'content-type, x-goog-api-key, api-revision, Api-Revision');
  if (req.method === 'OPTIONS') return res.status(204).end();

  const key = req.headers['x-goog-api-key'];
  if (!key) return res.status(400).json({ error: { message: 'missing x-goog-api-key' } });

  try {
    let upstreamUrl, init;
    if (req.method === 'POST') {
      upstreamUrl = UPSTREAM;
      // body may already be parsed (object) or raw — normalize to JSON string
      const bodyStr = typeof req.body === 'string' ? req.body : JSON.stringify(req.body || {});
      init = {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-goog-api-key': key, 'Api-Revision': API_REVISION },
        body: bodyStr,
      };
    } else if (req.method === 'GET') {
      const id = String(req.query.id || '').trim();
      if (!id) return res.status(400).json({ error: { message: 'missing id' } });
      upstreamUrl = `${UPSTREAM}/${encodeURIComponent(id)}`;
      init = { method: 'GET', headers: { 'x-goog-api-key': key, 'Api-Revision': API_REVISION } };
    } else {
      return res.status(405).json({ error: { message: 'method not allowed' } });
    }

    const upstream = await fetch(upstreamUrl, init);
    const text = await upstream.text();
    res.setHeader('Content-Type', 'application/json');
    return res.status(upstream.status).send(text);
  } catch (e) {
    return res.status(502).json({ error: { message: 'upstream_failed: ' + String(e && e.message || e) } });
  }
}
