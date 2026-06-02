# Results Page Spec (Foresight Oracle)

> A self-contained explainer of how the results / analysis page works — readable
> without opening `index.html`.
> Companions: overall methodology in `METHODOLOGY.md`; data-gathering & architecture
> in the handoff note at the top of `NOTES.md`. (Traditional-Chinese version: `RESULTS_PAGE_SPEC.md`.)

---

## 1. In one sentence

The results page renders **one structured prediction JSON** (produced by `askOracle`)
plus **one pool of numbered real evidence** (`buildEvidenceIndex`) into:
**current-state narrative → futures cone → deeper insights → live evidence → ideation studio.**
Every claim's "source" link is a piece of evidence the synthesis engine **explicitly cited by tag** —
it is never guessed after the fact.

---

## 2. The two core data objects

### (A) Numbered evidence pool — `buildEvidenceIndex(sig)` → `{ text, map }`
Numbers every **real signal** that was gathered, one tag per item:
- `[W#]` = a Claude web-search finding (carries a real leaf-page URL)
- `[M#]` = a prediction market (Polymarket/Kalshi — market-page URL + probability %)
- `[N#]` = a news article (GDELT — article URL)
- `[H#]` = a Hacker News thread (thread URL)

`text` = the numbered list fed to the synthesis engine (e.g. `[W3] SpaceX plans to IPO 6/12 … — https://...`).
`map` = `{ W3: {url, text}, M1: {...}, ... }` — used at render time to turn a tag back into a real URL.

### (B) Prediction JSON (output of `askOracle`; Claude acts as "domain expert + futurist")
**The field order IS the reasoning order (reasoning-first): analyze first, then derive the cone from it.**

```jsonc
{
  "topic":   "refined topic",
  "summary": "one vivid headline prophecy",
  "narrative": "current-state narrative (3–5 sentences weaving the latest, most relevant real info; the backbone of the whole prediction)",

  "drivers": [ { "text": "≤24-char driving-signal title", "src": ["W3","M1"] } ],   // 4–6 of them

  "depth": {                                   // deeper structure (Causal Layered Analysis)
    "systemicCauses": [ { "text": "structural force", "src": ["W2"] } ],            // evidence-backed
    "worldviews":     [ "competing assumptions / framings beneath the surface" ],   // interpretive
    "metaphor":       "one line capturing the underlying image"                     // interpretive
  },

  "crossImpacts": [                            // cross-impacts between forces
    { "pair": "Driver A × Driver B", "type": "reinforcing|tension|trigger", "note": "mechanism", "src": ["W2","M1"] }
  ],

  "horizons": [                               // the cone's events, in three time bands
    { "range": "3–6 months",   "headline": "...", "events": [ EVENT, ... ] },
    { "range": "6–12 months",  "headline": "...", "events": [ ... ] },
    { "range": "12–18 months", "headline": "...", "events": [ ... ] }
  ],

  "wildcard":    "a low-probability, high-impact but traceable black-swan",
  "wildcardSrc": ["W7"]
}

// EVENT =
{ "title": "possible event", "likelihood": "probable|plausible|possible",
  "fringe": 0-100, "rationale": "basis (cites real evidence)", "src": ["W5","N2"] }
```

**Hard rules (enforced in the prompt):**
- Every driver / event / wildcard / systemicCause / crossImpact **must carry `src`** (the evidence tags it relied on); no evidence → don't include it.
- `likelihood` follows evidence strength **and must agree with the matching market probability** (market ≥~40% → probable; low → possible).
- `fringe` is **inverse** to how well-corroborated the claim is (mainstream/multi-source → low, near the center axis; single/speculative → high, on the outer edge).
- Events must be consistent with `crossImpacts` (reinforcing → more probable, tension → more uncertain, trigger → placed in its horizon).

---

## 3. How sources / citations attach (the most-misunderstood part)

**There is exactly one path — precise, never guessed:**
1. The synthesis engine tags each node with `src: ["W3","M1"]` (it can see the numbered evidence pool).
2. At render time `attachEventSources()` uses `map` to turn `W3 → real URL`, stored as that node's `_sources`.
3. `eventSourcesHTML()` renders `_sources` as "依據 / basis" chips (show the domain, click to open the source).

**Important (fixed 2026-06):**
- **There is no more "guess the source by word overlap" fallback.** Previously, when a node's tags didn't
  resolve, the code token-matched the text against the whole source pool; a loose threshold (2 overlapping
  words) pinned **irrelevant** sources on claims. **Removed**: if `src` doesn't resolve, **no source is shown** (honest).
- `hostOf()` now rejects **invalid / truncated / hostless URLs** → no more "empty/broken" links.
- So a chip appearing ⇒ it is a source the synthesis engine **explicitly cited**, with a valid URL.

**Scout-card sources** take a different but equally precise path: a scout tags its finding with `#N`,
and `runScoutOnce` maps that back to the real URL of that numbered data item.

---

## 4. How the futures cone positions each dot

`plotCone(data)`: every event in every horizon becomes a dot.
- **X axis = time**: which horizon the event belongs to (`HORIZON_X` = 3–6 / 6–12 / 12–18 months).
- **Y axis = distance from the center axis** (represents uncertainty):
  `dist = LIK_FRAC[likelihood] × 0.45 + (fringe/100) × 0.55`
  - `LIK_FRAC` = probable 0.24 / plausible 0.52 / possible 0.8 → **more likely = closer to the axis**.
  - `fringe` 0–100 → **more fringe = closer to the outer edge**.
  - The weighted blend means "mainstream & high-probability" sits on the central axis while "niche & speculative" lands on the rim.
- A draggable time-handle extends/retracts the horizon; **clicking any dot highlights its event card → reveals that event's source chips.**

→ Dot positions are **not random**: driven by `likelihood` (tied to market odds / evidence strength) × `fringe`
(tied to corroboration), and the whole JSON is produced reasoning-first (drivers/depth/crossImpacts first, then the cone grows on top of them).

---

## 5. Section order on the page (DOM, top to bottom)

| Section | id | Content | Data source |
|---|---|---|---|
| Header | `resultTopic` / `resultSummary` / `resultNarrative` | topic / headline / **current-state narrative (backbone)** | `topic`/`summary`/`narrative` |
| **Futures cone** | `coneSvg` | dots = events; draggable time axis; clickable | `horizons` + `plotCone` |
| **Key drivers** | `signalsSection` | 2-column cards, each with "basis" chips | `drivers` |
| **Horizon cards** | `horizons` | 3 bands (short/mid/long), each 2–3 events (likelihood badge + rationale + basis) | `horizons` |
| **🔎 Deeper insights** | `insightsSection` | tabs: ⚡black-swan (default) / 🧊structure (CLA) / 🔗cross-impact | `wildcard`/`depth`/`crossImpacts` |
| (Deep Research panel) | `deepResearch` | only when deep mode drives it | Gemini Deep Research |
| **🔮 Futures Studio** | `futuresStudio` | 3 tones optimistic/neutral/black-swan → scenario story (+ HMW/actions for tech topics) | re-calls Claude on `lastResult` on demand |
| **Live evidence cards** | `newsCard`/`socialCard`/`trendsCard`/`wikiCard` | GDELT news / Reddit+Bluesky / Google Trends / Wikipedia | `sig.*` (raw real data, clickable) |
| **Scout signals** | `scoutFindings` | 5 scout-agent domain readings, each with "explored sources" | scout results |
| **Prediction markets** | `marketSource` | Polymarket + Kalshi market list (clickable) | `sig.markets` |
| **🔎 Verified sources** | `claudeSources` | the synthesis step's own web-search citations | sources returned by askOracle |

---

## 6. Short / mid / long-term predictions

These are the three `horizons`: **3–6 / 6–12 / 12–18 months**, all counted **from "today"** (`todayStr()` is fed into the prompt).
Each band has a headline + 2–3 events; events land on the cone by `likelihood`/`fringe` and on the time axis by `range`.
If the topic involves a dated event (a match / IPO / election), the prompt requires distinguishing
"before the event / during / aftermath" when arranging the bands.
Separately, `futuresStudio` offers three scenario tones — optimistic / neutral / black-swan — describing
**how this topic resolves**, as raw material for team ideation.
