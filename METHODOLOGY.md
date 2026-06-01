# Foresight Oracle — 方法論 (Methodology)

> 這份文件描述 Foresight Oracle 目前的 end-to-end 未來預測方法論，
> 用於對照市場上既有的 foresight / scenario-planning 框架。
> （與實作同步；若改了流程請一起更新。）

## 0. 核心理念 (Philosophy)

- **證據接地 (evidence-grounded)**：每一個論點都要能溯回一個真實、可點的來源；
  禁止 LLM 憑空捏造。沒有證據支撐的事件不放。
- **即時資料 (live signals)**：用預測市場、web search、新聞、社群、搜尋熱度等
  「現在正在發生」的訊號，而非靜態知識。聚焦近期。
- **完整溯源 (traceability)**：narrative → drivers → 未來錐事件 → wildcard，
  每一個節點都對映到它依據的真實來源連結。
- **模型各司其職**：Claude = 引導(understandTopic)＋蒐集(web search)＋綜合；
  Gemini = 深度研究 agent（Interactions API，是 Gemini 唯一會真正 grounding 的路徑）。
- **隨主題調整 (context-aware)**：偵察員角色、發想工具都依主題類型(競技/科技/政策…)動態調整。
- **誠實降級**：拿不到資料就誠實留白，不偽造（empty > fabricated）。

## 1. 兩種模式 (只差「蒐集」，分析引擎相同)

| | ⚡ 淺搜 (fast) | 🔬 深挖 (deep) |
|---|---|---|
| 蒐集 | 中央 API + 多查詢 Claude web search | Gemini Deep Research Agent（自主規劃→搜尋→閱讀數十源→引用報告） |
| 速度/成本 | 秒~分鐘、低 | 數分鐘、$1–3/次 |
| 之後 | 同一個 askOracle 分析引擎 → 未來錐 | 同一個 askOracle 分析引擎 → 未來錐 |

模式在「輸入主題時」就選定。

## 2. End-to-End 流程

1. **主題理解 (understandTopic, Claude)**：判讀主題真正在問什麼、展開檢索實體/同義詞、
   指派一支 **5 人偵察隊**（各有領域 + stance: hot 追主流確定 / niche 挖冷門早期 / mixed）
   + 一位**領域專家**身分。角色依主題類型調整：
   - 競技/選舉/賽事 → 賠率、戰力、傷病、賽程、誰會贏。
   - 科技/產品 → 技術成熟度、產品落地、**年輕世代/早期採用者**、**新興弱訊號**、競爭/監管。
2. **蒐集 (gather)**：
   - 中央 Tier-1 來源（並行、allSettled）：Polymarket、Kalshi、GDELT 新聞、Wikipedia 關注度、
     Bluesky、Google Trends、Hacker News。
   - `gatherWebMulti`：多組 Claude web search（主題＋實體＋各偵察員查詢）＋ 一條社群/年輕世代查詢
     (Reddit/HN/Gen Z) ＋ **一條專門的預測市場查詢**(讓 Claude 在脈絡中找到相關賠率＋報導)。
     每條發現要近期、附 leaf-page 真實 URL。
   - （深挖模式：Gemini Deep Research 取代上面，產出引用報告，餵進同一引擎。）
3. **編號證據池**：所有真實訊號編號 `[W#]`(web)/`[M#]`(市場)/`[N#]`(新聞)/`[H#]`(HN)，
   建立「編號 → 真實 URL」對映表。
4. **偵察員解讀 (5 agents)**：每位**讀同一包真實資料**，從自己的領域鏡頭挑訊號、解讀其意涵，
   句末標編號 → 對映回真 URL。**他們不自己上網**（解讀，不是各自搜尋，避免幻覺與限流）。
5. **綜合 (askOracle, Claude = 領域專家 + 未來學家)**，輸出結構化 JSON：
   - `narrative` 現況主敘事：3–5 句連貫骨幹，串起最新最相關的真實資訊。
   - `drivers` 關鍵驅動：4–6 條精簡訊號標題，各附 `src` 證據編號。
   - `horizons` × 3（3–6 / 6–12 / 12–18 個月），每段 2–3 個 `events`。
   - `wildcard` 黑天鵝 + `wildcardSrc`。
6. **預測框架（讓「點位反映證據」）**：
   - `likelihood` ∈ {probable, plausible, possible}，依證據強度判定，且須與對應市場機率一致
     （市場 ≥~40% → probable；低機率 → possible）。
   - `fringe` (0–100)：與「被佐證程度」成反比——主流多源佐證→低分(靠中軸)，單一投機→高分(外圍)。
   - 每個 event / driver / wildcard 都要 `src` 證據編號（無證據不放）。
   - **wildcard 方法論**：必須是「低機率高衝擊、且有跡可循」的尾端風險——從某個真實弱訊號/結構性脆弱
     外推、講得出因果機制、會實質改寫走向、不與既有 events 重複。不准隨機災難。
   - **深層結構 (depth, CLA)**：`systemicCauses`(撐起表面訊號的結構性力量，附 src) +
     `worldviews`(檯面下競爭的假設/典範/利益) + `metaphor`(底層隱喻)。超越「發生什麼」挖「為什麼、誰的視角」。
   - **交叉影響 (crossImpacts)**：2–4 組關鍵驅動/事件之間的交互——加乘 / 張力 / 觸發，附 src。
7. **視覺化：未來錐 (futures cone)**：
   - X 軸 = 時間 horizon；Y 軸（離中軸距離）= `LIK_FRAC[likelihood]×0.45 + fringe/100×0.55`。
   - 可拖曳時間軸把手；每個光點 = 一個事件；**點光點 → 顯示形成它的真實來源連結**。
   - **深層洞察 (tabbed section)**：未來錐底下一個「🔎 深層洞察」區，三個 tab——
     `⚡ 黑天鵝`(預設) / `🧊 深層結構` / `🔗 交叉影響`，把「表層預測底下的力量」收在一起，
     讓 demo 能一層層剝開、也保持頁面乾淨。
8. **未來工作坊 (Futures Studio, 發想)**：三種情境調性按鈕 **樂觀 / 中性 / 黑天鵝**；
   點一個 → Claude 用本次分析(narrative/drivers/events/真實訊號)生成「**這個主題會如何收場**」的
   身歷其境情境故事，錨定在問題見分曉的自然時點。**依主題動態取捨**：
   科技/產品/政策題另給 How Might We + 發想觸發 + 給團隊的下一步行動；
   競技/賽果類只給情境故事（context-aware 行動設計）。

## 3. 一句話定位

> **一個即時、證據接地、可全程溯源的「短期(18 個月)未來感知 + 情境發想」引擎**——
> 把活的訊號(市場/新聞/社群/搜尋)經多視角 agent 解讀，綜合成可視化的未來錐，
> 再轉成能帶團隊發想、可採取行動的情境故事與 How Might We。
