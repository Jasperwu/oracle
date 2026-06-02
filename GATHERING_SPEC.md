# 資料搜集規格書 (Data Gathering Spec)

> 給人或其他 AI 看的「我們怎麼搜集廣泛且高品質資訊」說明。
> 很多 AI 的搜集是「丟一個查詢」或「全部塞進去」→ 一堆雜訊。這份講清楚我們為什麼不一樣。
> 配套：結果頁看 `RESULTS_PAGE_SPEC.md`；整體方法論看 `METHODOLOGY.md`。

---

## 0. 核心原則(先記這四條)

1. **廣度來自「多個角度的查詢」，不是一個大查詢** —— 先理解主題、拆成多個互補面向，每個面向各自搜。
2. **品質來自「硬性門檻」** —— 每條發現都必須：①近期 ②附「具體文章(leaf page)」的真實 URL ③真的查到、不准編。
3. **用會真搜的工具** —— Claude `web_search` 真的會上網、回真實引用；**Gemini 的 `generateContent`+google_search 不會真搜、只幻覺(已棄用)**。
4. **誠實 > 量** —— 找不到可靠近期來源的那一條，**就不要寫**。寧缺勿濫。

---

## 1. 兩種模式（只差搜集，分析引擎相同）

| | ⚡ 淺搜(fast) | 🔬 深挖(deep) |
|---|---|---|
| 搜集 | 中央 API + 多查詢 Claude web search | Gemini **Deep Research Agent**(Interactions API：自主規劃→搜尋→閱讀數十源→引用報告) |
| 廣度/深度 | 廣、近期、秒~分鐘 | 更深、$1–3、數分鐘 |
| 之後 | 同一個 `askOracle` 分析引擎 | 同一個 `askOracle` 分析引擎 |

---

## 2. 淺搜的搜集管線(逐步)

### 步驟 0 — 先「理解主題」再搜（`understandTopic`，Claude）
不直接拿原始關鍵詞亂搜。先一次 Claude 呼叫：
- 展開**檢索實體 / 同義詞**(entities)——例：「SpaceX IPO」→ SPCX、Starlink、Elon Musk、SpaceX valuation…
- 組一支 **5 人偵察隊**，每位負責一個**互補面向**，並各自預擬 2–3 條**具體查詢**(含時效字詞)。
- 依主題類型調整面向(競技題→賠率/戰力/傷病；科技題→技術/落地/年輕世代/新興弱訊號/競爭監管)。
→ 這一步決定了「廣度」：之後的搜集會覆蓋多個角度，而不是同一批結果。

### 步驟 1 — 多查詢 Claude web search（`gatherWebMulti`）
把查詢分三類、用對應的分析師 persona 各自搜：
- **一般(general)**：keyword + entities + 各 scout 的查詢，去重後取前 ~5 條。
- **社群/新興(social)**：`"<主題> reddit OR hacker news discussion"`、`"<實體> emerging trend gen z early adopters"`
  → 用「社群與新興趨勢分析師」prompt，主動讀 Reddit 討論串、HN、論壇、X，抓**年輕世代/早期採用者**在做什麼、剛冒出的弱訊號。
- **預測市場(market)**：`"<主題> Polymarket OR Kalshi odds prediction market"`
  → 用「預測市場分析師」prompt，在脈絡中找相關賠率(市場頁本身 + 引用它的報導)。

**每條查詢都是一次真正的 Claude web search**(`web_search` 工具，maxUses 5)；**並行限流 2** 條(覆蓋所有面向、又不撞速率限制)。

### 步驟 2 — 硬性品質門檻（`fmtRule`，每條發現都要遵守）
- ① **聚焦最近 7 天**內的最新進展(或句末標日期)。
- ② 句末附上**該則資訊的「具體文章網址」(leaf page)** —— **不要**列表頁、首頁、搜尋頁、tracker。
- ③ **找不到可靠近期單篇來源的，就不要寫這一條。**

### 步驟 3 — 配對與去重
- `parseFindingsWithUrls`：每條 bullet 配上**它自己的** URL(不借別條的，避免來源錯配)。
- 跨所有查詢**聚合 + 去重**(發現用前 40 字、來源用 URL 去重)。
- 上限：~100 條發現 + ~120 個來源。

### 步驟 4 — 中央 Tier-1 來源（並行，`Promise.allSettled`）
同時抓七個**結構化、可點**的真實來源(任一掛掉不影響其他)：
Polymarket、Kalshi、GDELT 新聞(限英文 + 關聯度過濾)、Wikipedia 關注度、Bluesky(關聯度過濾)、Google Trends、Hacker News(關聯度過濾)。

### 步驟 5 — 編號證據池（`buildEvidenceIndex`）
把上面所有真實訊號編號 `[W#]`(web)/`[M#]`(市場)/`[N#]`(新聞)/`[H#]`(HN)，建立「編號 → 真實 URL」對映，餵給分析引擎。
分析時每個論點要標 `src` 編號 → 之後對映回真實來源(見 `RESULTS_PAGE_SPEC`)。

---

## 3. 為什麼這樣能「廣且高品質」

| 想要 | 我們怎麼做到 |
|---|---|
| **廣** | `understandTopic` 先拆出多個互補面向 + 每個 scout 的角度查詢 → 多角度覆蓋，不是同一批結果 |
| **新** | `fmtRule` 硬性要求近 7 天；中央 GDELT 限近 3 天 |
| **相關** | Claude 在脈絡中判斷相關性;中央 API 用 `maxRelevance` 過濾;市場/社群有專屬 persona |
| **可信/可查** | 每條發現都要附 leaf-page 真實 URL，否則丟掉;結構化來源本來就有 URL |
| **不重複** | 跨查詢去重(文字 + URL) |
| **不幻覺** | 只用會真搜的 Claude web_search;prompt 明令「只報實際查到的、不准編」 |

---

## 4. 別的 AI 常見的錯(我們刻意避開的失敗模式)

1. **一個大查詢就交差** → 淺、窄。 → 我們：多角度查詢。
2. **不限時效** → 撈到過時資訊。 → 我們：硬性近 7 天。
3. **不要求 leaf page** → 一堆列表頁/首頁/tracker。 → 我們：只收單篇文章 URL。
4. **每條不附來源** → 無法查證、容易混入腦補。 → 我們：沒來源就不寫。
5. **不過濾相關性** → 一堆離題雜訊。 → 我們：相關性過濾 + 脈絡判斷。
6. **相信「LLM grounding」其實沒真搜** → 幻覺(我們踩過這個坑，Gemini grounding 已棄用)。 → 我們：只用真搜工具。
7. **不去重** → 同一件事重複洗版。 → 我們：聚合去重。
8. **全塞給分析引擎** → 訊噪比低。 → 我們：編號 + 上限 + 由分析引擎按證據引用。

---

## 5. 工具選擇的真相（很重要）

- **Claude `web_search`**：**真的會上網搜尋並回傳真實 citations** → 淺搜的搜集主力。
- **Gemini `generateContent` + `google_search`**：實測**不會真搜、只從記憶幻覺**(groundingMetadata 永遠空、會掰假引用) → **已棄用,不要用它當搜集器**。
- **Gemini Deep Research Agent**(Interactions API)：是 Gemini **唯一**會真搜的路徑(自主規劃、跑數十次搜尋、讀數十源、回有引用的報告) → 深挖模式專用。

> 一句話：**先理解主題拆成多角度 → 各用「會真搜的工具」搜 → 每條都鎖近期＋leaf-page＋附來源 → 去重 → 編號餵給分析。**
> 廣度來自「多角度」，品質來自「硬門檻 + 真搜工具 + 誠實留白」。
