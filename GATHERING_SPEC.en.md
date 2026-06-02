# Data Gathering Spec (Foresight Oracle)

> How we gather **broad AND high-quality** information — for people or other AIs.
> Many AIs "gather" by firing one query or dumping everything → a pile of noise.
> This explains why we don't. (Traditional-Chinese version: `GATHERING_SPEC.md`.)
> Companions: `RESULTS_PAGE_SPEC.en.md`, `METHODOLOGY.md`.

---

## 0. Core principles (remember these four)

1. **Breadth comes from many angle-specific queries, not one big query** — understand the topic first, split it into complementary facets, search each.
2. **Quality comes from hard gates** — every finding must: ① be recent, ② carry a real URL to a *specific article (leaf page)*, ③ actually be found, never invented.
3. **Use a tool that actually searches** — Claude `web_search` really browses and returns real citations; **Gemini's `generateContent` + google_search does NOT actually search — it hallucinates (abandoned).**
4. **Honesty > volume** — if a finding has no reliable recent source, **drop it.** Quality over quantity.

---

## 1. Two modes (only gathering differs; same analysis engine)

| | ⚡ Shallow (fast) | 🔬 Deep |
|---|---|---|
| Gathering | Central APIs + multi-query Claude web search | Gemini **Deep Research Agent** (Interactions API: plans → searches → reads dozens of sources → cited report) |
| Breadth/Depth | broad, recent, seconds–minutes | deeper, $1–3, minutes |
| Then | the same `askOracle` engine | the same `askOracle` engine |

---

## 2. The shallow gathering pipeline (step by step)

### Step 0 — Understand the topic before searching (`understandTopic`, Claude)
We don't blindly search the raw keyword. One Claude call first:
- Expands **search entities / synonyms** — e.g. "SpaceX IPO" → SPCX, Starlink, Elon Musk, SpaceX valuation…
- Assembles a **team of 5 scouts**, each owning a **complementary facet**, each pre-writing 2–3 **specific queries** (with recency terms).
- Adapts the facets to the topic type (competition → odds/roster/injuries; tech → tech maturity/GTM/youth/emerging weak signals/competition & regulation).
→ This step creates the breadth: the gather then covers many angles, not one batch of results.

### Step 1 — Multi-query Claude web search (`gatherWebMulti`)
Queries are split into three kinds, each searched with a matching analyst persona:
- **general**: keyword + entities + each scout's queries, deduped, top ~5.
- **social / emerging**: `"<topic> reddit OR hacker news discussion"`, `"<entity> emerging trend gen z early adopters"`
  → a "community & emerging-trends analyst" prompt that actually reads Reddit threads, HN, forums, X for what **youth / early adopters** are doing and the weak signals just surfacing.
- **prediction market**: `"<topic> Polymarket OR Kalshi odds prediction market"`
  → a "prediction-market analyst" prompt that finds the relevant odds in context (the market pages themselves + the news citing them).

**Each query is a real Claude web search** (`web_search` tool, maxUses 5), run at **concurrency 2** (cover every facet without hitting rate limits).

### Step 2 — Hard quality gate (`fmtRule`, every finding obeys it)
- ① **Focus on the last 7 days** (or date the finding).
- ② Append **the specific article URL (leaf page)** for that fact — **not** a listing/home/search/tracker page.
- ③ **If there's no reliable recent single-article source, don't write that finding.**

### Step 3 — Pairing & dedup
- `parseFindingsWithUrls`: each bullet is paired with **its own** URL (never borrows another's, so a chip never mismatches its claim).
- Aggregate + dedup across all queries (findings by first 40 chars, sources by URL).
- Caps: ~100 findings + ~120 sources.

### Step 4 — Central Tier-1 sources (parallel, `Promise.allSettled`)
Simultaneously fetch seven **structured, clickable** real sources (one failing can't sink the rest):
Polymarket, Kalshi, GDELT news (English + relevance-filtered), Wikipedia attention, Bluesky (relevance-filtered), Google Trends, Hacker News (relevance-filtered).

### Step 5 — Numbered evidence pool (`buildEvidenceIndex`)
Number every real signal `[W#]` (web) / `[M#]` (market) / `[N#]` (news) / `[H#]` (HN) and build a tag → real-URL map, fed to the analysis engine.
During analysis every claim tags its `src` numbers → later resolved back to real sources (see `RESULTS_PAGE_SPEC.en.md`).

---

## 3. Why this is both broad and high-quality

| Want | How we get it |
|---|---|
| **Broad** | `understandTopic` first splits the topic into complementary facets + each scout's angle queries → multi-angle coverage, not one batch |
| **Fresh** | `fmtRule` hard-requires the last 7 days; central GDELT is limited to ~3 days |
| **Relevant** | Claude judges relevance in context; central APIs use `maxRelevance` filtering; markets/social have dedicated personas |
| **Verifiable** | every finding must carry a leaf-page URL or it's dropped; structured sources already carry URLs |
| **Non-redundant** | dedup across queries (text + URL) |
| **No hallucination** | only the truly-searching Claude web_search is used; the prompt orders "report only what you actually found, never invent" |

---

## 4. Common mistakes (failure modes we deliberately avoid)

1. **One big query and done** → shallow, narrow. → Us: multi-angle queries.
2. **No recency** → stale info. → Us: hard last-7-days.
3. **No leaf-page requirement** → piles of listing/home/tracker pages. → Us: single-article URLs only.
4. **No per-finding source** → unverifiable, easy to slip in fabrication. → Us: no source → not written.
5. **No relevance filter** → off-topic noise. → Us: relevance filtering + in-context judgment.
6. **Trusting "LLM grounding" that doesn't actually search** → hallucination (we hit this; Gemini grounding is abandoned). → Us: real-search tools only.
7. **No dedup** → the same thing repeated. → Us: aggregate + dedup.
8. **Dump everything into the analysis engine** → low signal-to-noise. → Us: numbered + capped + cited-by-evidence by the engine.

---

## 5. The truth about tool choice (important)

- **Claude `web_search`**: **actually browses and returns real citations** → the shallow gatherer.
- **Gemini `generateContent` + `google_search`**: empirically **does not actually search — it hallucinates from memory** (groundingMetadata always empty, invents fake citations) → **abandoned; do not use it as a gatherer.**
- **Gemini Deep Research Agent** (Interactions API): the **only** Gemini path that truly searches (plans, runs dozens of searches, reads dozens of sources, returns a cited report) → deep mode only.

> In one line: **understand the topic and split into angles → search each with a tool that actually searches → gate every finding on recency + leaf-page + a source → dedup → number it for the analysis.**
> Breadth comes from "many angles," quality comes from "hard gates + real-search tools + honest omission."
