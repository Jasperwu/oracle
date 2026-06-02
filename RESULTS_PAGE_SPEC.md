# 結果頁規格書 (Results Page Spec)

> 給人或其他 AI 看的「結果分析頁怎麼運作」說明。讀這份就懂，不必啃 `index.html`。
> 配套：整體方法論看 `METHODOLOGY.md`；蒐集/架構看 `NOTES.md` 交接便條。

---

## 1. 一句話

結果頁把「**一份結構化 JSON 預測**(由 `askOracle` 產生)＋**一池編號好的真實證據**(`buildEvidenceIndex`)」
渲染成：**現況主敘事 → 未來錐 → 深層洞察 → 即時佐證 → 發想工作坊**。
每個論點的「依據」連結，都是**綜合引擎自己標的證據編號**對映回真實 URL —— 不是事後猜的。

---

## 2. 兩個核心資料物件

### (A) 編號證據池 `buildEvidenceIndex(sig)` → `{ text, map }`
把所有蒐集到的**真實訊號**編號，每筆一個 tag：
- `[W#]` = Claude web search 的發現（含真實 leaf-page URL）
- `[M#]` = 預測市場（Polymarket/Kalshi，含市場頁 URL + 機率%）
- `[N#]` = 新聞（GDELT，含文章 URL）
- `[H#]` = Hacker News（含討論串 URL）

`text` = 餵給綜合引擎的編號清單（如 `[W3] SpaceX 預計 6/12 上市… — https://...`）。
`map` = `{ W3: {url, text}, M1: {...}, ... }`，給渲染時把 tag 換回真實 URL。

### (B) 預測 JSON（`askOracle` 輸出，Claude 當「領域專家＋未來學家」）
**產生順序就是推理順序(reasoning-first)：先分析、再據此推未來錐。**

```jsonc
{
  "topic":   "精煉主題",
  "summary": "一句富畫面感的總綱",
  "narrative": "現況主敘事(3–5句，串起最新最相關真實資訊，是整個預測的骨幹)",

  "drivers": [ { "text": "≤24字的驅動訊號標題", "src": ["W3","M1"] } ],   // 4–6 條

  "depth": {                                   // 深層結構 (CLA)
    "systemicCauses": [ { "text": "結構性力量", "src": ["W2"] } ],         // 接證據
    "worldviews":     [ "檯面下競爭的假設/視角" ],                          // 詮釋層
    "metaphor":       "一句底層隱喻"                                       // 詮釋層
  },

  "crossImpacts": [                            // 交叉影響
    { "pair": "驅動A × 驅動B", "type": "加乘|張力|觸發", "note": "機制", "src": ["W2","M1"] }
  ],

  "horizons": [                               // 未來錐的事件，分三個時段
    { "range": "3–6 個月",  "headline": "...", "events": [ EVENT, ... ] },
    { "range": "6–12 個月", "headline": "...", "events": [ ... ] },
    { "range": "12–18 個月","headline": "...", "events": [ ... ] }
  ],

  "wildcard":    "低機率高衝擊、有跡可循的黑天鵝",
  "wildcardSrc": ["W7"]
}

// EVENT =
{ "title": "可能事件", "likelihood": "probable|plausible|possible",
  "fringe": 0-100, "rationale": "依據(引用真實證據)", "src": ["W5","N2"] }
```

**硬性規則(寫在 prompt 裡)**：
- 每個 driver / event / wildcard / systemicCause / crossImpact **都要 `src`**(引用的證據編號)；沒證據的不放。
- `likelihood` 依證據強度，**且要與對應市場機率一致**(市場≥~40%→probable；低→possible)。
- `fringe` 與「被佐證程度」**成反比**(主流多源→低分靠中軸；單一投機→高分靠外圍)。
- events 要與 `crossImpacts` 一致(加乘→更可能、張力→更不確定、觸發→放對應 horizon)。

---

## 3. 來源 / 引用怎麼接（這是最常被誤解的部分）

**只有一條路，精準、不猜：**
1. 綜合引擎在每個節點標 `src: ["W3","M1"]`（它看得到編號證據池）。
2. 渲染時 `attachEventSources()` 用 `map` 把 `W3 → 真實 URL`，存成該節點的 `_sources`。
3. `eventSourcesHTML()` 把 `_sources` 畫成「依據」chip（顯示網域、點開原文）。

**重要(2026-06 修正)**：
- **沒有「字詞重疊猜來源」的 fallback 了**。以前對不到編號時會拿文字去跟來源池做 token 比對，
  門檻太鬆(2個字重疊)就掛上 → 造成「不相關 URL」。**現已移除**：對不到 `src` 就**不顯示來源**(誠實)。
- `hostOf()` 會擋掉**無效/截斷/沒網域的 URL** → 不再出現「空的/壞的」連結。
- 所以一個 chip 出現 ⇒ 它是綜合引擎**明確引用**的、且 URL 有效的真實來源。

**scout 卡片的來源**走另一條但同樣精準：scout 在發現裡標 `#N` → `runScoutOnce` 對映回該編號資料項的真實 URL。

---

## 4. 未來錐 (futures cone) 怎麼定位每個點

`plotCone(data)`：每個 horizon 的每個 event 畫成一個光點。
- **X 軸 = 時間**：事件屬於哪個 horizon（`HORIZON_X` = 3–6 / 6–12 / 12–18 個月）。
- **Y 軸 = 離中軸距離**(代表不確定性)：
  `dist = LIK_FRAC[likelihood]×0.45 + (fringe/100)×0.55`
  - `LIK_FRAC` = probable 0.24 / plausible 0.52 / possible 0.8 → **越可能越靠中軸**。
  - `fringe` 0–100 → **越邊緣越靠外緣**。
  - 兩者加權混合：所以「主流且高機率」落在中央軸、「冷門投機」落在外圍。
- 可拖曳時間軸把手延伸/收回視野；**點任一光點 → highlight 對應事件卡 → 看到它的「依據」來源**。

→ 點位**不是隨機**：由 `likelihood`(綁市場機率/證據強度) × `fringe`(綁佐證度) 決定，且整個 JSON 是
reasoning-first 產生(先 drivers/depth/crossImpacts，未來錐長在其上)。

---

## 5. 結果頁區塊順序（DOM，由上到下）

| 區塊 | id | 內容 | 資料來源 |
|---|---|---|---|
| 標題列 | `resultTopic` / `resultSummary` / `resultNarrative` | 主題 / 總綱 / **現況主敘事(骨幹)** | `topic`/`summary`/`narrative` |
| **未來錐** | `coneSvg` | 光點 = 事件，可拖時間軸、可點 | `horizons` + `plotCone` |
| **關鍵驅動訊號** | `signalsSection` | 2 欄卡，各帶「依據」chip | `drivers` |
| **時段卡** | `horizons` | 3 段(短/中/長)，每段 2–3 事件(likelihood badge + rationale + 依據) | `horizons` |
| **🔎 深層洞察** | `insightsSection` | tabs：⚡黑天鵝(預設) / 🧊深層結構(CLA) / 🔗交叉影響 | `wildcard`/`depth`/`crossImpacts` |
| (深度研究面板) | `deepResearch` | 只在深挖模式驅動 | Gemini Deep Research |
| **🔮 未來工作坊** | `futuresStudio` | 三鈕 樂觀/中性/黑天鵝 → 情境故事(+科技題另給 HMW/行動) | 即時用 `lastResult` 再呼叫 Claude |
| **即時佐證卡** | `newsCard`/`socialCard`/`trendsCard`/`wikiCard` | GDELT 新聞 / Reddit+Bluesky / Google Trends / Wikipedia | `sig.*`(原始真實資料，可點) |
| **AI 偵察員訊號** | `scoutFindings` | 5 個 scout 的領域解讀卡，各帶「探索來源」 | scout 結果 |
| **預測市場** | `marketSource` | Polymarket + Kalshi 市場列(可點) | `sig.markets` |
| **🔎 查證來源** | `claudeSources` | 本次綜合 web search 的引用列 | askOracle 回的 sources |

---

## 6. 短 / 中 / 長期預測

就是 `horizons` 三段：**3–6 / 6–12 / 12–18 個月**，全部**從「今天」起算**(`todayStr()` 餵進 prompt)。
每段有 headline + 2–3 個事件；事件依 `likelihood`/`fringe` 落在未來錐上、依 `range` 落在時間軸上。
若主題涉及有明確日期的事件(賽事/IPO/選舉)，prompt 要求分清「事件前 / 進行中 / 結果後」安排各段。
另有 `futuresStudio` 提供「樂觀/中性/黑天鵝」三種**這個主題如何收場**的情境故事，供團隊發想。
