# 對話與決策時間線 (NOTES.md)

> 這份檔案保存我們合作的**脈絡與決策過程**,讓任何新 session 都能無痛接上。
> 規範見 `CLAUDE.md`。**最新的記在最上面。**

---

## 2026-05-29 · 強化 extractJSON:scout 全空 + 綜合 JSON 解析爆掉

**現象(實測「Space X」)**:動態組隊**成功**(火箭哥/星鏈姐/任務官/競局者/馬斯克觀=SpaceX 專屬),
但 5 個 scout **全部回空**,最後綜合報錯
`Expected ',' or ']' after array element in JSON at position 3583`。

**根因**:`extractJSON` 太脆——只會 `JSON.parse` 整段。但 web search 開著時 Claude 回的 JSON 常有:
尾隨逗號、被 search prose 包住、smart quotes、或 **maxTokens 用完被截斷**(position 3583=截在陣列中間)。
scout 解析失敗 → `catch` 回 `signals:[]`(全空);綜合解析失敗 → 直接拋錯(紅字)。
5 scout 各自 web search 回大段 JSON,失敗率飆高。

**修法**:
- `extractJSON` 四段式 fallback:① 直接 parse ② `repairJSON`(去 fence/尾逗號/smart quote)
  ③ `sliceBalanced`(從 prose 中切出最外層 {...}) ④ `closeTruncated`(截斷搶救:丟掉殘缺片段、
  補回未閉合的 "/]/} → 救回已完成的欄位)。
- 調高 token 上限降低截斷機率:scout 1200→1800、綜合 3000→4500。
- Node 實測 5 種失敗模式(尾逗號/fence/prose/截斷/smart quote)全部救回;
  截斷案例能救回 topic/summary/drivers + 第一段完整 horizon。

---

## 2026-05-29 · 加三個免費 CORS 友善來源(GitHub / Stack Overflow / Bluesky)

**背景**:使用者想要 Google Trends / X / TikTok 趨勢。釐清**純前端的真正關卡是 CORS + 付費/門禁**:
- Google Trends：無官方 API、非官方爬蟲會被 CORS 擋 → 需後端,且脆。
- X：API $100/月起 + OAuth + 不支援瀏覽器 CORS。TikTok：僅需審核的 Research API。
→ 這三個**純前端拿不到**;後端代理能解 CORS 但解不了 X/TikTok 的錢與門禁。

**決策(使用者選 A）**:先接**免費、免金鑰、CORS 友善**的來源,不動純前端架構、零部署風險。
後端代理(Vercel serverless 補 Google Trends)列為之後的第二階段,未做。

**已接(都走現有 `fetchXXX` + `maxRelevance` 過濾模式)**:
- `fetchGitHub`：repos search,`sort=stars`,當「開發動能」。
- `fetchStackEx`：Stack Overflow search/advanced,`sort=activity`,當「技術問答熱度」。
- `fetchBluesky`：`public.api.bsky.app` searchPosts,`sort=top`，當「社群即時聲量」(X 的替代)。
- 三者都進 `signalDigest`(餵 scout)與 `buildSynthPrompt`(餵綜合);`sig` 多了 `github/stack/bluesky`。

**已知限制 / 風險**:
- ⚠️ 沙箱擋外網,**無法當場驗證這三個端點的回傳格式與 CORS**,務必實機測。
- GitHub 免金鑰限 10 req/分;Bluesky/StackEx 失敗都 graceful 回 []。
- **結果頁尚未為這三個來源做顯示卡片**(render 只顯示 markets/news/HN/wiki);它們目前只影響分析,
  不在結果頁露出。要不要顯示待使用者決定。
- GitHub/StackOverflow 偏技術主題;非技術主題(如 NBA)它們通常回空,屬正常。

## 2026-05-29 · 釐清 scout 架構 + 輕量版「各自 web search」

**使用者的心智模型 vs 實際**:使用者以為 5 個 scout 各自去爬不同來源(news/forums/學術/總經)。
**實際**(已澄清):資料是 `runPrediction` **中央抓一次**固定 5 來源(PM/Kalshi/GDELT/HN/Wiki),
把**同一包** `signalDigest` 發給全部 scout;scout 的「領域」只是**解讀視角(persona)**,
不是專屬資料管線。唯一能各自抓新資料的途徑是 **web search**。
→ 這就是「Google Cloud」時有 scout 交白卷的原因:它對應的硬資料(如預測市場)是空的,
prompt 又允許「沒相關就略過」,於是回空;且該次 `understandTopic` 疑似失敗退回 `DEFAULT_SCOUTS`
(截圖隊名=通用隊),連帶 entities 也沒展開。

**Synthesis 確認**:`buildSynthPrompt` 本來就把「5 scout 訊號 + 原始 PM/news/HN/Wiki」**整包**
餵給**單一** `askOracle`,一次推演 3–6/6–12/12–18 → **本來就是 cross-pollinate**。

**決策(使用者拍板)**:做**輕量版**,保留 prompt persona:
1. `runScout`:web search 開啟時，**每個 scout 主動以自己的領域視角下不同查詢**(maxUses 2→3),
   讓「不同 agent 搜不同東西」成真。
2. **放寬交白卷**:即使沒現成即時資料，也要基於該領域專業給 2–4 個有根據的判斷；
   只有主題與領域真的無關才回空。
3. **synthesis 明確要求跨領域交叉連結**(政策×市場、研究×社群…),不要分開條列。

**取捨/風險**:5 個 scout 各自 web search → API 量大增,**更容易撞 429**。現有護欄:
CONCURRENCY=2 限流 + 429 退避重試。若現場仍常撞,後手是調回 maxUses 或關 web search。
**未做完整版**(接 Reddit/arXiv/總經等真多元來源,工程大且前端 CORS 受限)。

## 2026-05-29 · Polymarket 改「search 優先 + 分頁 fallback」

**動機**:與其拉 2000 筆回來猜，不如直接用平台的全文搜尋只要相關的。
**作法**:
- 新增 `GAMMA_SEARCH = .../public-search`。`searchPolymarket(queries)` 用 keyword + entities
  打全文搜尋（每詞 limit_per_type=20、events_status=active），攤平 events 底下的 markets、去重。
  這能抓到「market 的 question 不含關鍵字、但所屬 event 含」的盤口（NBA 季後賽常見）。
- 抽出共用 `rankPolymarket()` + `normalizePolymarket()`，search 與分頁兩條路共用。
- `fetchMarkets`：① search 優先（`requireScore:false`，因 search 已做相關性）；② 空了或失敗
  → 退回原本的分頁 + 相關性過濾（`requireScore:true`）。失敗有保底不會壞。
- Kalshi 維持 cursor 分頁（公開 API 無全文搜尋）。

**風險**:沙箱擋外網，**無法當場驗證 public-search 的真實回傳格式（欄位/巢狀）**。
程式對 `data.events[].markets` 與 `data.markets` 都做了防呆，但**務必實機驗證**；
若 search 打歪會自動 fallback 到分頁，不致全空。

---

## 2026-05-29 · 候選池太小:NBA 市場只剩 1 個 → 分頁加寬

**回饋(實測「NBA playoff 2026」)**:預測市場只剩 1 個，但 Polymarket NBA 版有一大堆。
**根因(不是評分 bug)**:Node 實測新評分下 NBA 市場全拿 30 分（「NBA」是特殊詞，直接命中），
沒被誤殺。真正問題是抓取只取 `limit=500&order=volumeNum`＝「全站成交量前 500 大」。
Polymarket 有數千個活躍市場；FIFA 世界盃單國盤口成交量 3000–4500 萬，穩居前 500 一抓一堆；
NBA 季後賽盤口成交量沒那麼高，多排在 500 名外，**根本沒進候選池**，只有最高量的 1 個擠進來。

**修法**:
- `fetchMarkets` 改成**平行分頁抓 4 頁**（offset 0/500/1000/1500，約 2000 筆），加寬候選池後再過濾；
  同分時改按成交量排序。
- `fetchKalshi` 同患（只抓前 1000 open markets，且未按量排序）→ 改用 **cursor 分頁**最多抓 4 頁。
- 沙箱擋外網無法直接打 API 驗證；評分邏輯已用 Node 確認 NBA 市場得分正常（非評分問題）。

**待辦**:速度（understandTopic + 分頁多打幾次 API）；先求對，speed 之後優化。

---

## 2026-05-29 · 修相關性評分 bug:無關高熱度市場混入 + HN 雜訊

**回饋(實測「mlb power ranking」)**:預測市場竟全是 FIFA World Cup（且機率多為 0%），
明明 Polymarket/Kalshi 有很多 MLB 盤口；HN 也出現與 MLB 無關的科技內容。

**根因(同一個 bug）**:`relevanceScore` 對「單一 token 弱命中」給分太鬆。
entity「World Series」的 `world` 在「FIFA World Cup」裡 `hasWord` 命中 +5 → 達門檻 5，
FIFA 市場混入；又因成交量極高（4000 萬）排序排前，把真正的 MLB 市場擠掉。
HN 同理：Algolia 寬鬆 OR 比對 + HN 是科技論壇，回一堆只中 ranking/power 的科技文章。

**修法**:
- 重寫 `relevanceScore`：加 `STOPWORDS`（world/league/cup/power/ranking/年份…通用詞）；
  **單一通用詞單獨命中不再算數**（return 0），必須「整片語命中」或「有特殊詞命中」
  或「≥2 token 同時出現」。整片語命中直接 30 分。
- `fetchHN` 對結果**套相關性過濾**（`maxRelevance ≥ 5`），濾掉科技雜訊；entity fallback
  改成「合併去重後一起過濾」。
- Node 實測驗證：FIFA→0（濾掉）、World Series→30、MLB Power Rankings→30、Yankees→20；
  HN 科技噪音 DROP、真 MLB 內容 KEEP。

**待辦**:速度（understandTopic 多一次呼叫）—使用者覺得「慢了點」，先求準，speed 之後再優化。

---

## 2026-05-29 · 綜合 agent 升級為「領域專家 + 未來學家」雙重身分

**確認(使用者問)**:分析短/中/長期的是**一個** agent(`askOracle`,一次 Claude 呼叫產出三段),
原本只設了 futurist 角色、**缺領域專家身分** —— 收集端已動態化(scout),但分析端仍是通用 futurist。

**修法**:`understandTopic` 多回一個 `expert`(主題專屬專家身分,例「資深 NBA 籃球分析師」);
`askOracle(keyword, sig, scoutResults, expert)` 的 system prompt 動態拼成
「你同時是一位『${expert}』,也是一位未來學家…請拿出該領域真正的專業判斷」。
`expert` 為空(understandTopic 失敗 / fast mode)時退回純 futurist。改動小、無新增 API 呼叫。

---

## 2026-05-29 · 修核心:主題理解 + 動態偵察隊(資料方向 & 分析品質)

**回饋(實測「nba power rank」)**:分析方向全錯 —— 不是聯盟各隊趨勢/選秀/正在進行的
總冠軍,而是去探討「power rank 的 ML 模型」「做個排名工具」,毫無用處;預測市場明明
有很多今年冠軍的盤口,卻只跑出 1 個。使用者點出:應該有**動態 agent** 去收集**正確、
最相關**的資訊並做深入分析,而不是套科技/產品框架。

**根因(已逐行查證)**:
- A. `SCOUTS` 寫死成科技/產品團(research=arXiv/GitHub、culture=Product Hunt),
  且每訊號強制填「對產品/設計意涵」→ 忠實地答錯問題。
- B. 市場抓取字面比對:「nba power rank」對「Will the Spurs win the 2026 NBA Finals?」
  只命中 `nba`(+5),真正相關的冠軍市場分數低被濾掉 → 只剩 1 個。

**使用者決策**:選 **A — 完全動態,讓 Claude 當場組隊**;馬上做。

**實作(7 步,已上線)**:
1. `SCOUTS` → `DEFAULT_SCOUTS`(通用 fallback)+ `let activeScouts`(動態隊伍)。
2. 全部引用改 `activeScouts`(runScouts / 板子 / 文案 / 計數)。
3. 新增 `understandTopic(keyword)`:一次 Claude 呼叫 → `interpretation` + `entities` + `scouts`。
4. `runScout` 改吃動態 `domain/task/angle` + `signalDigest`,移除「產品/設計意涵」。
5. `maxRelevance(primary, secondary, queries)`:對 keyword + 所有 entities 取最高分。
6. 抓取吃 entities:市場用 maxRelevance(門檻 5、取 8);GDELT/HN/Wiki 原詞無果用 `entities[0]` fallback。
7. `runPrediction`:深掃第一步先 `understandTopic`(設好隊伍 + 拿 entities),再抓資料。
   綜合 prompt 加「緊扣主題、別硬拗成做產品」。

**成本**:深掃多一次輕量 Claude 呼叫(understandTopic, maxTokens 900);quality 換速度,值得。
**未動**:結果頁、fast mode(快速模式不經 understandTopic,維持原樣)。

---

## 2026-05-29 · 探員「先召喚待命」改善等待體驗

**回饋**:深掃時卡在「正在召喚神諭」很久,探員才 pop out;中間沒有回饋像當機。
**根因**:`runPrediction` 先 `await Promise.all([5 個 fetch])`(Polymarket/Kalshi/GDELT/HN/Wiki)
才 `initScoutBoard()`。`Promise.all` 等最慢的源(Kalshi limit=1000、Wiki 連打兩次 API)回來,
且 fetch 沒 timeout,任何一個慢就把探員出場時間整個拖住。

**決策(使用者拍板,最小改動)**:**只把 initScoutBoard() 提前到抓資料之前**,
探員立刻 pop out 站成一列「待命」,背景同時抓資料 —— 把等待變成「刻意的登場」。
**背後抓資料邏輯完全不動**(不加 timeout、不改順序)。
文案:待命階段「召喚偵察員小隊… / N 個 agent 待命中」,開掃才切「掃描邊緣訊號」。

**未採用(留作後手)**:給每個 fetch 加 8s timeout —— 這次刻意不做,先看「先召喚」是否就夠。

---

## 2026-05-29 · 推翻黑色 mission control → 探員改在同一頁 pop out

**使用者回饋(看實機截圖)**:深掃時 UI「分兩層」、會跳成黑色頁面,很奇怪;
而且探員排成「4 個 + 下面再 1 個」也很怪。明確要求:**在原本的頁面上 pop out 探員就好,
不要轉跳、不要換黑色頁面**。

**根因**:
- 「分兩層」= `runPrediction` 在深掃時對 overlay 加 `.mission-mode`,整頁從淺色切成黑色終端,
  外加頂部標題列 + 底部終端狀態列 —— 視覺上像跳到另一個畫面。
- 「4+1」= 5 個探員 cell 各 116px,但容器 `min(560px)` 放不下 5 個 → 第 5 個 wrap 到下一行。

**修正(定案)**:
- **拿掉** `.mission-mode` 深色主題、頂部 `mission-top` 標題列、底部 `mission-foot` 終端狀態列、
  以及 mission clock (`startMissionClock`/`stopMissionClock`/`#missionClock`)。
- 探員直接浮在**原本優雅的淺色水晶球頁**上,`.pixie-cell` 改成暖陶土色系。
- 版面 `flex-wrap: nowrap` + `flex:1` 讓 5 個探員**整齊排成一列**(窄螢幕才 wrap)。
- pop-out 動畫 `scoutPopIn`(帶 overshoot 的縮放浮現),狀態列改回繁中
  (待命 → 掃描中▍ → ✓ N 個訊號);底部低調顯示「偵察員已回報 k/5」。
- 這**推翻** `CLAUDE.md` 原決策 #2 的「深色終端 mission control」方向;決策 #2 已改寫。

---

## 2026-05-29 · 撞到 API 429 速率限制 → 決定花錢升 tier

**現象**:demo 輸入「AI overview」時,網站跳 `Claude API 錯誤 429`:
org 速率限制為**每分鐘 30,000 input tokens**(model `claude-sonnet-4-6`,即 Tier 1 入門額度)。

**根因(已查證,與程式邏輯無關)**:`runScouts` 用 `Promise.all` **一次並行 5 個 scout**
(index.html:1264);若 web search 開著,每個 scout 把搜尋結果塞回 input,5 並行 → 同一分鐘
input tokens 暴衝,加上之後的綜合 (askOracle) 大請求,撞破 30k/min。

**決策**:**走 C — 花錢升 tier**(到 console 買 credits 抬高 30k/min 天花板)。
**不改程式**,維持 5 並行 + web search 的現狀。

**備註(將來若再撞)**:升 tier 只抬天花板,「瞬間爆量」本質仍在。若日後 demo 再撞 429,
備援方案是 A(scout 限流:一次最多 2 個 + 讀 `retry-after` 自動退避重試)、
D(scout 預設關 web search,只綜合那步開)。目前**未採用**,留作後手。

---

## 2026-05-29 · 持久化記錄機制 + mission-control 完成

**背景**:使用者發現新視窗讀不到舊對話,且擔心對話遺失。釐清根因:
雲端容器即用即拋,對話逐字稿無法跨 session,**唯一能存活的是 commit/push 進 repo 的內容**。
決定建立 `CLAUDE.md`(長期規則/決策) + `NOTES.md`(脈絡/時間線)兩份檔案做持久化記憶,
並約定「隨時更新並保留對話記錄」。

**也釐清了那個 API 400 error**:
`messages.25.content.19: thinking ... blocks cannot be modified`。
這是 extended thinking + tool use 的限制 —— 送回 API 的歷史中,最後一則 assistant 訊息的
thinking/redacted_thinking block 必須與原始回應一字不差(含 signature)。
框架層若重組/截斷/丟簽章就會 400。**與網站程式無關,git 歷史乾淨,工作未受影響。**

**驗證過的事實**:
- 三方 SHA 一致 (`HEAD` = `origin/branch` = `origin/main` = `4127449`),工作樹乾淨。
- JS 語法 OK,mission-control 所有關鍵元素都在。

---

## (更早) · pixel agent mission-control 深掃轉場

**決策**:talk demo 優先衝**趣味性**,做 pixel 探員 + 「反差」mission control。

**一個誠實的微調(已和使用者對齊)**:參考圖裡的 agents 是**待在格子裡配狀態列**(監控台),
不是真的滿場跑。最終做成「mission control 監控台 + 派遣/回報動態」,精神同樣是
Power Ranger 那種團隊感,但對 talk 更專業、盲做也更穩。

**實作內容(深掃時的轉場 = 深色 agent 監控台)**:
- 上方終端標題列 `◇ FORESIGHT · AGENT TEAM` + 即時時鐘 (`#missionClock`)。
- 中央水晶球當「核心」,深色背景上發光。
- 下方 5 隻 pixel 方塊探員 (`creatureSVG`,grid-of-rects),各配狀態列:
  `STATUS: idle → scanning▍ → ✓ N signals`。
- 探員掃描時抖動/閃爍,回報完成變綠 + 打勾;底部狀態列顯示「scouts returned k/5」。
- 全部回報 + 綜合完成 → 切回**優雅的結果頁**(反差)。
- pixel 角色是方塊格子,盲做也能精準。**結果頁維持原樣不動。**

---

## (更早) · design actions 要 context-aware(尚未實作)

關鍵分辨,已記入 `CLAUDE.md` 決策 #1:
design actions「只在相關主題才浮現」。「AI agents 的未來」需要它;「NBA 2026 總冠軍」不需要,
現有體驗本身就夠有趣。這是之後做 design actions 功能 ① 的硬性前提。

---

## 演進時間線(回填,依 git commit 還原)

依 `git log` 的實際 commit 順序整理,作為更早脈絡的存底(由舊到新):

1. **`93028b9` Add files via upload** — 網站初版上傳。
2. **`607698f` Fix modal not closing after saving API key** — 修 BYOK 金鑰輸入框存檔後沒關閉的 bug。
3. **`180b5dd` Add cupped hands to oracle orb and link Polymarket sources**
   — 水晶球加上捧著的雙手造型;結果開始連結 Polymarket 預測市場來源。
   *(註:這對手後來被推翻 —— 見第 6 點。)*
4. **`bd9c35b` Make the futures cone interactive and add Kalshi markets**
   — futures cone 變成可互動;訊號來源再加 Kalshi 市場。
5. **`543cf12` Redesign orb scene and futures cone in hand-drawn line-art style**
   — 確立**手繪線稿 + 暖陶土色**的美術方向,水晶球場景與 futures cone 一起重畫。
6. **`5cebfb7` Replace orb hands with sparkles; add time-scrubber to futures cone**
   — **推翻第 3 點的「手」**,改成環繞水晶球的 sparkles (✦);futures cone 加上可拖曳的時間軸 scrubber。
   呼應 `CLAUDE.md` 決策 #4:徒手畫複雜造型(手)容易翻車,改用可精準掌控的視覺。
7. **`556b0f2` Add multi-agent fringe-signal scanning** — 加入 5 個 scouts 的多 agent 邊緣訊號掃描。
8. **`4127449` Add pixel-art agent mission-control transition (deep scan)** — pixel agent mission-control 深掃轉場(見上面的詳細記錄)。
