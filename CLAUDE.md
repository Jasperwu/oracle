# Foresight Oracle · 專案備忘 (CLAUDE.md)

> 這份檔案是**跨 session 的長期記憶**。每個新的 Claude Code session 會自動讀它。
> 容器是即用即拋的 —— 對話本身不會留下,只有 commit/push 進 repo 的東西能存活。
> **規則:每當我們做出新的設計決策、完成或推翻某個方向,就更新這份檔案,並一起 commit。**
> 詳細的對話脈絡與決策時間線記在 `NOTES.md`。

## 這是什麼

一個單檔 (`index.html`)、零後端的互動式「未來神諭」網站,給一場 **talk / demo** 用。
使用者輸入一個主題,網站讀取真實訊號(預測市場、新聞、社群熱度、Wikipedia 關注度),
再用 Claude API 綜合推演出未來 18 個月的情境,以「futures cone(未來錐)」視覺化呈現。

- **語言/受眾**:介面繁體中文;觀眾是 talk 的聽眾,重點是**趣味性 + 專業感**。
- **架構**:純前端單檔 HTML/CSS/JS,無 build step。使用者自帶 Anthropic API 金鑰 (BYOK),
  瀏覽器直接打 Anthropic API (`anthropic-dangerous-direct-browser-access`)。
- **美術風格**:手繪線稿 (hand-drawn line-art) + 暖陶土色 (clay) 調性;結果頁優雅、沉穩。

## 核心設計決策(現行,務必遵守)

1. **「行動設計 (design actions)」要 context-aware** —— 只在相關主題才浮現。
   主題是「AI agents 的未來」時 design actions 很有意義;主題是「NBA 2026 總冠軍」時就不該硬塞。
   這是之後要做 ① design actions 功能時的硬性前提。**目前尚未實作**。
2. **深掃時探員在「同一頁」pop out,不換頁、不跳黑底**(2026-05-29 修正定案)。
   pixel 探員直接浮現在原本優雅的淺色水晶球頁上、排成整齊一列(`flex-wrap: nowrap`),
   各配狀態列(待命 → 掃描中▍ → ✓ N 個訊號)。
   ⚠️ **已推翻**先前的「深色終端 mission control / 整頁切黑」方向 —— 那會造成突兀的
   「分兩層」跳轉,使用者明確不要。也不要頂部終端標題列或底部終端狀態列。
3. **結果頁維持原樣,不要動** —— futures cone + horizons 的優雅結果頁是定案的,
   除非明確要求,不要改它。深掃轉場的「反差」正是建立在結果頁的優雅上。
4. **盲做要選可精準掌控的視覺** —— pixel 角色是 grid-of-rects,盲做也不會壞;
   避免徒手畫複雜造型(例如手)那種容易翻車的東西。

## 目前狀態

- **已完成**:① 多 agent 邊緣訊號掃描 ② 探員在同一頁 pop out(淺色,非黑底)
  ③ scout 限流 + 429/529 退避重試 ④ **主題理解 + 動態組隊**(見下)。
- **待辦 / 下一步候選**:context-aware 的 design actions(決策 #1,尚未開工)。

## 主題理解 + 動態偵察隊(2026-05-29 定案,核心架構)

**問題**:scout 曾被寫死成「科技/產品團」(arXiv/GitHub/Product Hunt)且強制填
「對產品/設計意涵」→ 打「nba power rank」會去找排名 ML 模型、做 App,文不對題;
市場抓取是字面比對,真正相關的冠軍市場分數過低被濾掉,只剩 1 個。

**解法(現行)**:
- `understandTopic(keyword)`:深掃**第一步**,一次 Claude 呼叫讀懂主題,回傳
  ①`entities`(展開的檢索實體/同義詞)②一支 5 人**動態偵察隊**(`activeScouts`)
  ③`expert`(主題專屬的領域專家身分,例:資深 NBA 籃球分析師)。
  失敗則 fallback 到 `DEFAULT_SCOUTS`(通用 5 隊,非科技專屬)。
- **綜合 agent 雙重身分**:短/中/長期是**同一個** agent(`askOracle`)一次產出;其 system
  prompt 動態拼接成「領域專家(`expert`)+ 未來學家(futurist)」——既懂門道又會推演;
  `expert` 為空時退回純 futurist。
- **抓取吃 entities**:`fetchMarkets` 走**分頁** /markets(offset 0/500/1000/1500)+
  `rankPolymarket`(`requireScore:true` 相關性過濾,沒相關回 [])。
  ⚠️ 曾試 Gamma `/public-search` 優先,但其回傳缺正確 event slug → 市場卡片不可點,
  且會混入無關市場 → **已移除,只用分頁**(slug/URL 可靠)。`fetchKalshi` 用 cursor 分頁 +
  `maxRelevance`。`fetchGdelt/fetchHN/fetchWikiTrend` 在原關鍵詞無果時用 `entities[0]` fallback;
  HN 結果再套相關性過濾濾掉科技雜訊。
  `relevanceScore` 有 `STOPWORDS`:通用詞(world/league/power/ranking…)單獨命中不算數。
  市場卡片:`m.url` 有才渲染成可點 `<a>`,沒有則 `<div>` —— 所以 slug 必須正確。
- `runScout` 吃動態 `domain/task/angle`,並把 `signalDigest`(市場/新聞/HN/Wiki 摘要)
  餵給每位探員;移除寫死的「產品/設計意涵」,改問「對主題未來走向代表什麼」。
  **失敗處理**:`runScoutOnce` 為單次嘗試;`runScout` attempt 1 帶 web search,失敗→attempt 2
  **去掉 web search** 降級重試,兩次都掛才回 `error:true`。UI 區分「⚠ 連線失敗」(`.errored`)
  與「— 無訊號」(真沒資料),不再把出錯偽裝成無訊號。
- **架構真相**:資料是 `runPrediction` **中央抓一次**(固定 5 來源),**同一包**發給全部 scout;
  scout 的領域只是**解讀 persona**,不是專屬資料管線。**輕量版**(2026-05-29):web search 開啟時
  每個 scout **各自以領域視角下不同查詢**(maxUses 3);prompt **放寬**成「沒現成資料也要靠領域知識給判斷,
  別輕易交白卷」。⚠️ 5 scout 各自 web search → API 量大、易撞 429,靠 CONCURRENCY=2 + 退避重試擋。
- **綜合本就 cross-pollinate**:`buildSynthPrompt` 把「全部 scout 訊號 + 原始資料」整包餵單一 `askOracle`;
  已明確要求「跨領域交叉連結」(政策×市場、研究×社群…),非分開條列。
- 綜合 prompt (`buildSynthPrompt`) 加上「緊扣主題、別硬拗成做產品」的硬性指示。
- **硬性原則**:分析必須**緊扣使用者輸入的主題本身**,不得硬拗成不相干領域(尤其別預設「做產品」)。

## 程式結構速查 (index.html, 單檔 ~1800 行)

- **5 個 scouts**:定義在 `const SCOUTS`(約 L1238)。
  id: `research` 🔬 / `markets` 📊 / `culture` 💬 / `policy` ⚖️ / `contrarian` 🎲。
- **訊號擷取**:`fetchMarkets`(Polymarket)、`fetchKalshi`、`fetchGdelt`(新聞)、
  `fetchHN`(Hacker News)、`fetchGitHub`(開發動能)、`fetchStackEx`(Stack Overflow)、
  `fetchBluesky`(社群即時聲量,X 替代)、`fetchWikiTrend`(Wikipedia pageviews)。
  後三者(2026-05-29 加)是免費、免金鑰、CORS 友善的來源,只進分析、**結果頁尚無顯示卡片**。
  ⚠️ Google Trends/X/TikTok 純前端拿不到(CORS+付費/門禁);後端代理列為未做的第二階段。
- **Claude 呼叫**:`callClaude()` (L1200) → `runScout()` / `askOracle()`(綜合)。
- **深掃探員 pop out**:`initScoutBoard` / `updateScout` / `creatureSVG`
  (pixel 角色,grid-of-rects SVG)。探員浮在原本的淺色 overlay 上(`.scout-board`,
  `flex-wrap: nowrap` 一列五個,`.pixie-cell` 暖陶土色);`#missionFootCount`
  顯示「偵察員已回報 k/5」。**已無** mission-mode / mission clock / 終端標題列。
- **結果頁**:`render()` / `plotCone()`(futures cone)/ `initConeScrubber()`(時間軸拖曳)。
  `renderScoutFindings` 顯示各 scout 訊號 + **「探索來源」chips**(`scoutSourcesHTML`/`hostOf`,
  取 `r.sources` 去重抽網域,可點開原文);降級的 scout 標「離線判讀」。
- **快速模式 (fast mode)**:跳過深掃,保留優雅的淺色 orb;深掃才進 mission control。

## 工作流程規範

- **開發分支**:`claude/future-prediction-site-lsrm0`。commit 後 push 該分支,
  目前流程是再 fast-forward 合進 `main` 並 push。
- **驗證**:改完用 `node --check` 對 `<script>` 內容做語法檢查(repo 內有現成做法)。
- **不要**自作主張開 PR,除非使用者明確要求。
- **保密**:不要把模型 ID 寫進 commit / 程式碼 / 任何推上 repo 的產物。

## 已知的非程式問題

- 曾遇到 `400 ... thinking blocks ... cannot be modified`:這是 extended thinking + tool use
  時,送回 API 的歷史裡 thinking block 被改動所致,**與本網站程式無關**,沒污染 git 歷史。
- **新視窗讀不到舊對話是正常的**(容器即用即拋)。跨 session 的記憶靠這份檔案 + `NOTES.md`。
