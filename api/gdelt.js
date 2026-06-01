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
  const target = `https://api.gdeltproject.org/api/v2/doc/doc?${params}`;
  // Each fetch gets its own hard timeout so a slow GDELT can never blow past
  // Vercel's 10s function budget (which used to surface as a 504 with no CORS
  // header). Whole budget: 2 attempts x 4s + 1s backoff < 10s.
  const fetchOnce = async (ms) => {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), ms);
    try { return await fetch(target, { headers: { Accept: 'application/json' }, signal: ctrl.signal }); }
    finally { clearTimeout(timer); }
  };
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'public, max-age=120'); // 2-minute cache
  try {
    let text = '', ok = false;
    for (let attempt = 0; attempt < 2; attempt++) {
      let upstream = null;
      try { upstream = await fetchOnce(4000); } catch { upstream = null; } // timeout/network
      if (upstream) {
        text = await upstream.text();
        if (upstream.status !== 429) { ok = text.trim().startsWith('{'); break; }
      }
      if (attempt < 1) await sleep(1000);
    }
    // Always return 200 + valid JSON + CORS so the frontend degrades to "no
    // news" gracefully instead of a CORS error or a bare 504.
    return res.status(200).send(ok ? text : JSON.stringify({ articles: [] }));
  } catch (e) {
    return res.status(200).send(JSON.stringify({ articles: [] }));
  }
}
