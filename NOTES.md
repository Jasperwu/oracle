# 對話與決策時間線 (NOTES.md)

> 這份檔案保存我們合作的**脈絡與決策過程**,讓任何新 session 都能無痛接上。
> 規範見 `CLAUDE.md`。**最新的記在最上面。**

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-02 · 第十六輪 / 訊號擴充批次①②③ + 反單一文化「廣撒網窄下注」 · 待實機驗證）

**一句話**：依「廣撒網、窄下注」原則做了**一批訊號改善**，**已上 main、等使用者實機 A/B 驗證**；不行就一鍵退回。
分支 `claude/github-branch-sync-UhrqL` ＝ `main`。**還原點 `restore/stable-2026-06-02` = `87d2652`(這批之前的穩定版)**。

> 🔙 **若這批 quality 不行 → 退回指令**：`git push origin restore/stable-2026-06-02:main --force`(使用者不會用 terminal，他說「退回」就由你執行)。

**背景脈絡(重要,別忘了使用者的核心顧慮)**：使用者要擴充訊號**填補盲點**(現缺:經濟基本面/資本流向/創新管線;偏 attention 而少 fundamentals)，
但**極度在意兩件事**：① 別讓加了新訊號後「所有預測都塌成金融/技術/基建底層更新」(單一文化 monoculture)；② 別為了平衡而變得空泛、無法實際運用。
**對齊結論(專家框架)**：多樣性是**輸入端**紀律(免得瞎)、不是**輸出端**配額(會變空泛)→ **「廣撒網、窄下注」**：輸入求多元、輸出求具體。

**這批做了什麼(3 顆獨立 commit,可單獨 revert)**：
1. **綜合 prompt 加「第二原則：廣撒網窄下注」**：證據量多≠重要、別被好量化的東西綁架、寧具體可證偽勿四平八穩、防蒙蔽靠 wildcard/crossImpacts「壓力測試」而非維度配額。
2. **證據池每類軟上限 `balanceWeb`(防數量輾壓)**：`WEB_KIND_CAP`(general .6/social .32/market .2/geo .22/capital .18)；**兩段式**(pass1 守上限讓少數類&新 facet 進得來、pass2 backfill **不縮小池子**→無退步)；用在 `buildEvidenceIndex`(40)+`collectSignalItems`(80)。web 發現在 `gatherWebMulti.one()` 標 `kind`；log 出 `組成 general=.. social=.. capital=..`(可觀測)。
3. **加 geo + capital 兩條 web facet**：`lens`=國際/非英語視角(去英美偏)+資本動向(募資/M&A/IPO,領先指標)。tasks 升到約 10 query(concurrency 2,+1 輪延遲)。

**🔬 驗證協定(待使用者做)**：5 主題測試組——humanoid robots(純科技)/NBA 2026 Finals(競技·測技術源**沒漏進**非技術題)/TikTok(文化年輕·測**沒被金融洗版**)/台灣半導體(地緣)/Bitcoin(金融·測**沒塌成金融獨白且夠具體**)。
rubric 6 項:具體可用性／切題／不被單一訊號主導／沒瞎(跨域)／證據紮實／整體可用度。**科學陷阱**:gatherWebMulti 即時上網→同主題兩次資料不同,純前後比會混入隨機差異;嚴謹做法是同主題多跑取平均、或日後加「同資料 A/B 開關」。使用者把輸出貼回，你按 rubric 評分→**贏才留、平/輸就退回**。

**⏸️ 這批刻意「沒做」(留待驗證過再單獨開批)**：arXiv / Metaculus / 金融基本面等**新結構化 fetcher**——沙箱無法驗證 CORS/欄位、且本身加重金融/技術偏向、會混淆 quality 歸因。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-02 · 第十五輪 / 文案誠實化 + logo 修正 + 社群訊號釐清）

**一句話**：這一輪做了**對外文案誠實化、header logo 修正、社群訊號架構釐清 + 移除空卡**。
分支 `claude/github-branch-sync-UhrqL` ＝ `main`，**已用 GitHub MCP 確認過 main 真的是最新**。最新 commit `fbba819`（或更新）。

> 🔧 **部署/同步鐵則（照舊）**：commit → push branch → 再 `git push origin <branch>:main`。Pages + Vercel 都從 main 部署。
> 本地 `origin/main` 可能過期 → 用 `mcp__github__list_branches`(owner=jasperwu repo=oracle) 看真值。
> ⚠️ **PR 建不起來是正常的**：因為已 fast-forward 進 main，branch 與 main 同一個 commit，GitHub 回「No commits between」。這個流程本就不靠 PR。
> 📌 **規範自省**：本份 CLAUDE.md 要求「做完決策就主動更新 CLAUDE.md/NOTES.md 並 commit」——**不要再反問使用者要不要更新，直接做**。

**這一輪做了什麼**：
1. **landing 文案誠實化**：原本硬保證「即時讀取 **Polymarket** 預測市場與社群訊號」→ 改「**即時上網蒐集**新聞、社群動態、預測市場與關注度趨勢」；
   eyebrow `PREDICTION MARKETS · SOCIAL SIGNALS · FUTURIST AI` → `LIVE WEB SIGNALS · PREDICTION MARKETS · FUTURIST AI`。理由：蒐集主力是 web search，Polymarket 只是其一、不一定有。
2. **header logo 修正**：`◇ Foresight Oracle` 原本連到 `https://jasperwu.github.io/`（跳出去變個人網站，錯的）→ 改成站內 `#brandHome` click handler，回 app 起始畫面（不清關鍵詞）。用站內 reset 而非固定 URL，Pages(`/oracle/`)+Vercel(根) 都不會錯。
3. **社群訊號架構釐清（重要，已寫進 CLAUDE.md）**：Reddit 直抓**已停用**(`Promise.resolve([])`，API 穩定 403，`sig.reddit` 恆空)；Bluesky 直抓仍跑但不穩(常被 `maxRelevance>=5` 濾空)；
   **社群 sentiment/論壇/討論主力＝`gatherWebMulti` 的 2 條社群查詢**(寫死、必跑、隨主題客製、回真實引用 URL)。
4. **社群查詢字串擴充（名實相符）**：原本只 `reddit OR "hacker news" discussion`(prompt 卻說涵蓋論壇/X→名不副實)→ 改 `reddit OR "hacker news" OR forum OR X (Twitter) discussion sentiment`。⚠️ X 有登入牆，實際覆蓋仍有限。
5. **移除「💬 社群即時聲量」結果頁卡片**：Reddit 恆空 + Bluesky 不穩 → 幾乎不顯示。移除 HTML/`el`/render 三處（destructure 也清掉 reddit,bluesky）。**保留 `fetchBluesky`**——它仍進 `collectSignalItems` 證據池餵綜合引擎，移卡不影響蒐集。
6. **市場熱度／深度（volume24hr + liquidity）入庫並當信心權重**：`normalizePolymarket` 與 Kalshi normalize 新增 `vol24`(近24h成交量)+`liquidity`(流動性/深度)。
   ① 證據文字帶「總量／近24h／流動性」金額(`collectSignalItems`)；② `buildSynthPrompt` 新增指示「市場熱度/深度＝信心權重」(深市場→高信心/低fringe、薄市場→弱訊號、近24h放大＝即時動能要點名)；
   ③ 結果頁市場卡為「近24h 成交量最高」者加 `🔥 近24h $X` 標籤(`.market-hot`)+ volume 加 tooltip 顯示三項金額拆解。⚠️ Gamma/Kalshi 的 `volume24hr`/`volume_24h`/`liquidity` 欄位需實機 console 確認有值。
   ⚠️ 已知偏誤：用 volume 加權會放大 Polymarket 的美國/加密圈偏斜(熱門題訊號更強、冷門/非英語題更弱)——對應待辦 #2「來源偏誤改善」。
7. **影音/年輕世代平台 facet(訊號擴充 Phase 1 · 零新增成本)**：`gatherWebMulti` 第 2 條社群查詢**就地擴充**(不新增查詢→不增延遲/API量)：
   `${ent} emerging trend gen z young early adopters` → `${ent} youtube OR tiktok OR twitch OR podcast gen z young creators emerging trend`;sysSocial prompt 也點名 YouTube/TikTok/Twitch/podcast。讓年輕世代訊號真的搆得到影音平台,不只文字論壇。

**🛡️ 訊號擴充的安全框架(定案,務必遵守)**：在動任何訊號擴充前已建還原點 **`backup/pre-signal-expansion` = `850f522`**(穩定 main)。
一鍵還原:`git push origin backup/pre-signal-expansion:main --force`。五條鐵律:①只加不改不刪(不碰現有 7 來源)②故障安全(新源 try/catch+回[]+非 load-bearing,沿用 allSettled)③一來源一 commit 可單獨 revert ④主題閘門(niche 源由 understandTopic 依主題開關,守「緊扣主題」)⑤逐步驗證(每加一個用 SpaceX/NBA/台積電 跑 before/after 看 console log)。
路線:Phase1 零風險查詢 facet(✅影音/年輕世代已做、🌍地理多元待做、💰資本/募資待做)→ Phase2 獨立 fetcher(arXiv/Metaculus,主題閘門)→ Phase3 金融基本面 → Phase4(暫緩:真實機率定位光點/環境感測)。

**還可做（沿用第十四輪候選，未做）**：① backcasting/偏好未來 ② 來源偏誤改善 ③ 對得上市場的事件直接用真實機率% 定位光點。⏳ 全站英文化仍是「功能凍結後才做」。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第十四輪 / 收尾 + 規格書 + 來源修正）

**一句話**：框架已成熟、使用者很滿意；這一輪做了**穩定性 audit + 清死碼 + 寫對外規格書(中英) + 修「來源亂掛」**。
最新 commit `9125f5a`（或更新）。分支 `claude/notes-handoff-review-UXYuR` ＝ `main`，**已用 GitHub API 確認過 main 真的是最新**。

> 🔧 **部署/同步鐵則(務必照做)**：流程是 **commit → push 到 branch → 再 `git push origin <branch>:main`**。
> GitHub Pages(jasperwu.github.io/oracle) + Vercel(oracle-bice) **都從 main 部署**，不推 main 線上就是舊的。
> ⚠️ 本容器的 `origin` 是 proxy；**本地 `origin/main` 可能顯示過期**。要確認真實狀態，用 **GitHub MCP**
> (`mcp__github__list_branches` owner=jasperwu repo=oracle) 看真 GitHub——之前有別的 session 因本地過期而誤判「main 是舊的」，其實不是。

> ⏳ **最後一步(先別做)**：全站**英文化**(UI + prompt 輸出語言)。在那之前維持繁中。
> 規模評估：UI 可見字串約 127 個(prompt 內部指令不必翻，只翻 8 處輸出語言開關)；雙語切換約 1 天、單向英文約半天。
> 建議**功能凍結後再做**(現在還在改 → 雙語會雙倍維護)。用詞(樂觀/中性/黑天鵝)英文也好翻，沿用。

**這一輪做了什麼**：
- **scout 狀態**：「待命」→ 5 個各顯示不同的「定位中/前往訊號源/整裝出發/鎖定座標/啟程中…」(脈動點點)，不再像卡住。
- **穩定性 audit**：el 參照全對得上、處處 try/catch + allSettled、429 退避、JSON 防截斷 → 無致命缺陷。
- **清死碼 ~130 行**：移除 fetchGitHub/StackEx/Reddit、marketBlock/newsBlock/buzz/github/stack/bluesky/redditBlock、
  SCOUT_SCHEMA、GEMINI_MODEL_FALLBACK、GITHUB_SEARCH/STACKEX_SEARCH/REDDIT_SEARCH。(`buildSourcePool` 現也幾乎沒用了，可再清。)
- **🔑 修「來源亂掛」**(重要)：`attachEventSources` 以前對不到 src 編號時會 **token 字詞重疊 fallback**(門檻只要 2 字)
  → 掛上不相關/錯誤來源。**已整個移除**：來源只來自綜合引擎明確標的 `[W#]/[M#]` 編號 → 對映回真 URL，對不到就**不顯示**(誠實)。
  `hostOf` 收緊：擋掉無網域/截斷/非 http 的 URL → 不再有空的/壞的 chip。**一個 chip 出現 = 明確引用且 URL 有效。**
- **對外規格書 ×4(新增)**：`RESULTS_PAGE_SPEC.md`/`.en.md`(結果頁/分析/溯源/未來錐定位)、
  `GATHERING_SPEC.md`/`.en.md`(搜集方法：多角度查詢+硬門檻+真搜工具)。給其他 AI 看就懂，不必啃 index.html。

**Gemini 現況(使用者還在想去留)**：淺搜「蒐集」已全跟 Gemini 無關(Claude web search + 中央 API)；
Gemini 只剩 ① scout「解讀」(runScoutOnce provider='gemini'，省 Claude 額度，沒 key 則 fallback Claude) ② Deep Research(深挖)。

**還可做(使用者選過、未做)**：① backcasting/偏好未來(工作坊加「🎯你想要的未來」) ② 來源偏誤改善(多地區/語言查詢+多元度標示)
③ 對得上市場的事件直接用真實機率% 定位光點。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第十三輪 / 集大成 · 框架已成熟）

**一句話**：經過一整天密集迭代，整套 end-to-end 未來預測框架**已成熟、使用者滿意**。
分支 `claude/notes-handoff-review-UXYuR` ＝ `main`（同步，最新 commit 約 `7ee443b` 一帶）。
**完整方法論看 `METHODOLOGY.md`（這是現行架構的真相，CLAUDE.md 本體已部分過時，以 METHODOLOGY.md 為準）。**

> ⏳ **最後一步(使用者定，先別做)**：整個 demo 網站最後會**全站英文化**(UI + prompts 輸出語言)。
> 在那之前一律維持繁體中文。**收尾才做，不要提前動。** 使用者說目前用詞(樂觀/中性/黑天鵝等)英文也好翻，沿用。

**這一整天的重大轉向 / 現況（濃縮）**：
- **Gemini grounding 已死、棄用**：`generateContent`+google_search 不真搜、只幻覺(實證+官方文件)。
  Gemini 現在只剩兩用途：`understandTopic`(其實是 Claude，見下) **沒有**——勘誤：understandTopic 一直是 **Claude**；
  Gemini 真正剩的只有 **Deep Research Agent**(Interactions API，唯一會真搜的 Gemini 路徑，深挖模式用)。
- **蒐集主力＝Claude web search**：`gatherWebMulti` 跨多查詢(主題+entities+scout queries + 1 社群/年輕世代 + 1 預測市場)，
  並行限流 2，回真實 leaf-page URL。**市場數據改靠這條**(Claude 在脈絡中找賠率)，原始爬蟲卡片降為加分項。
- **模式開頭就選**：⚡淺搜 / 🔬深挖(`runDeepPrediction`：先快 pass 出即時錐 → 自動接 Deep Research 重繪)。
- **證據紀律 + 完整溯源**：編號證據池 `[W#]/[M#]/[N#]/[H#]`；drivers/events/wildcard/depth/crossImpacts 都要 `src`；
  程式把 src/#N 對映回真 URL(`attachEventSources`)；點未來錐的點/各卡 → 顯示真實來源 chip。
- **結果頁結構**：主敘事(骨幹) → 關鍵驅動(2欄卡) → 未來錐(likelihood×fringe 定位，可拖時間軸) →
  **🔎 深層洞察(tabbed：⚡黑天鵝預設 / 🧊深層結構CLA / 🔗交叉影響)** → 即時佐證卡 → **🔮 未來工作坊**。
- **未來工作坊**：三鈕 樂觀/中性/黑天鵝 → 生成「主題如何收場」情境故事(錨定自然時點、從分析長出來)；
  **依主題動態**：科技/產品/政策另給 HMW+下一步；競技/賽果只給故事。
- **reasoning-first**：綜合 JSON 順序＝narrative→drivers→depth→crossImpacts→**horizons**→wildcard，
  讓未來錐「長在」分析之上 + events 要與 crossImpacts 一致。`askOracle` maxTokens=**8000**(防截斷)。
- **HN/youth**：Hacker News 重新啟用(中央抓取，科技題有料)；社群查詢含 Gen Z/早期採用者。

**還可做（使用者選過、尚未做的強化候選）**：
- ① backcasting/偏好未來(未來工作坊加「🎯你想要的未來」→ 里程碑+施力點+signposts)。
- ② 來源偏誤改善(understandTopic 出 regions/langs + 多元視角查詢 + 「來源多元度」標示)——大多隱形後端。
- ③ 讓「對得上市場的事件」直接用真實機率% 定位光點(更直接吃數據)。

**環境/規範**：沙箱連不了外網→所有 API 行為靠使用者實機驗證；GitHub Pages(jasperwu.github.io/oracle)+
Vercel(oracle-bice) 都從 main 部署，有 1–2 分鐘 lag，改完提醒 hard refresh + 看 console
`[central]`/`[gatherWebMulti]`/`[deep-research]` log。流程：commit→push branch→ 再 push 進 main。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第十二輪 / 預測框架 + 完整溯源）

> ⏳ **最後一步(使用者定，先別做)**：整個 demo 網站最後會**全站英文化**(UI + prompts 的輸出語言)。
> 在那之前一律維持繁體中文。**這是收尾才做的事**，不要提前動。

> 🆕 **未來工作坊 (Futures Studio，2026-06-01 加)**：模式改成開頭就選後，結果頁的「啟動深度研究」CTA 退役
> (深研面板只在深挖模式驅動;`resetDeepResearchPanel` 改成整塊隱藏、`runDeepResearch` 才 unhide)。
> 原位置換成 `#futuresStudio` 發想工具:**三種情境調性按鈕(樂觀/中性/黑天鵝)** → 點一個 → 一次 Claude 呼叫
> (`generateFuturesStudio`，用 `lastResult` 的 narrative/drivers/events/wildcard 當底) → 回 JSON
> `{story, hmw[], provocations[], actions[]}`。**動態取捨**:story 一律有;hmw/provocations/actions 只在
> 「可被設計/行動」的主題(科技/產品/商業/政策)才給,競技/賽事類只給 story(prompt 內建此判斷)。
> `lastResult` 在 `renderForecast` 設定。這就是 CLAUDE.md 決策 #1「context-aware 行動設計」的落地。

SpaceX IPO 測試品質明顯起來(主敘事扎實、市場對、cone 乾淨)。使用者問「點是不是隨便點/有沒有框架」。本輪:
- **預測框架**(`buildSynthPrompt`):每個 event 的 rationale 必須點名真實證據(優先市場機率如「Polymarket 44%」/多來源);
  likelihood 依證據強度且要與對應市場機率一致;fringe 與佐證度成反比;emerging/edge 放遠 horizon 給高 fringe 但要有線索。
  → cone 點位(Y=LIK_FRAC×0.45+fringe×0.55)現在綁證據而非直覺。
- **主敘事視覺強化**:`.results-narrative` 加陶土左框 + 標籤「現況主敘事 · 這個預測的依據」。
- **完整溯源**:新增 `buildSourcePool`(彙整所有真實 {text,url}:web findings/市場/新聞/scout sources/cited)+
  `attachEventSources`(事件 title+rationale 與來源池做 token 重疊比對,CJK 逐字+latin 逐詞,掛 top3)+
  `eventSourcesHTML`(事件卡底「依據」chip)。`renderForecast(data, sources, pool)` 兩條路徑都傳 pool。
  → 點 cone 上的點(會 highlight 對應卡)即可看到形成它的真實連結。

**待辦/可續**:① news=0(GDELT 對某些題目空)、trends ✗(Google 擋)仍是已知弱點。② emerging/edges 仍靠 prompt 帶,未獨立欄位。
③ 事件→來源是 token 比對(近似),非 LLM 明確標注;若要更精準可讓 askOracle 直接輸出每個 event 的來源 index。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第十一輪 / 主敘事 + 功能透鏡重設計）

使用者架構級回饋(cone 不錯但 agent 差、角色空轉、來源對不上、敘事不知所云、缺主敘事)。
拍板「**全部重設計**」+「**市場相關性低就隱藏**」。本輪做了:
- **新增「現況主敘事」**:`buildSynthPrompt` 加 `narrative` 欄位(3–5 句連貫最新現況+關鍵驅動,緊扣真實情報),
  askOracle JSON 多回 narrative;結果頁標題下新增 `#resultNarrative`(.results-narrative)顯示,`renderForecast` 填入(經 stripCites)。
- **scout 改「功能透鏡」**:scoutPrompts 改成「緊扣事件本體+最新、每條語句完整講『訊號→對結果意涵』、5–10 條、#N 引用」。
- **來源誠實**(上一 commit):移除亂配 citations;gather 要求近 7 天 + leaf page、配不到不掛。
- **市場隱藏**:rankPolymarket/fetchKalshi 門檻拉到 `qOnly>=8 && score>=16` + prob<0.97 → 跨運動/已決/冷門洗版的卡會直接不顯示(寧空勿錯)。

**待辦/可續**:① 若 score>=16 太嚴導致市場常空,再調。② understandTopic 角色已夠核心向,但若仍空轉可再針對「主題類型」分流角色模板。③ Google Trends 仍 best-effort(Google 擋)。④ emerging/edge cases 目前靠 narrative+wildcard+fringe,未獨立成欄位(可再加 emerging[]/edges[])。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第十輪 / World Cup 實測修五點）

實測 "2026 FIFA World Cup"(scout 9/8/10 條、逆勢 12 sources,有起來了)。修:
1. **預測市場顯示一堆 0% 冷門隊**(烏茲別克/紐西蘭…)而非熱門 → `rankPolymarket`/`fetchKalshi` 排序加
   **prob desc tiebreak**(同 relevance 時熱門優先)。championship outcome 市場不再被冷門洗版。
2. **`(#27、#28)` 編號噪音**(讀者看不到、對不上)→ 新 `stripRefs()` 在 `renderScoutFindings` 把編號從
   **顯示文字**拿掉(底部 source chips 仍在;#N→url 映射照舊在 runScoutOnce 做)。
3. **敘事截斷**(「金州勇士隊在」)→ gather maxTokens 2600→3500、scout 3000;`parseFindings` 丟掉
   <12 字的尾巴碎片;render 再濾 >6 字。
4. **agent sources 不一致(有些 0)**→ `gatherWebMulti` backfill 改**循環**該次 citations(`ci++ % len`),
   每條發現都拿得到真 url → scout #N 多半對得上。
5. **Google Trends 還是沒出** → 多半是 Google 擋非官方 endpoint(serverless IP)。`[central]` log 會顯示
   trends ✗。**無官方 API,難可靠修**;目前 best-effort 優雅降級。考慮之後拿掉或標「實驗性」。

⚠️ 部署延遲:使用者常測到舊版。每次改完提醒 hard refresh + 看 console `[central]` / `[gatherWebMulti]` / `[deep-research]` log。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第九輪 / 修四個實測 bug）

**實測 "nba 2026 finals" 淺搜**(110 findings/47 sources 進來了),使用者回報 4 問題,逐一修:
1. **scout 只有 1–3 條** → scoutPrompts 加「盡量 6–12 條」、scout maxTokens 2048→3000。
2. **scout 來源接不上(#N→null)** ← 真因:web 發現 item 的 `url` 是 null(findings/sources 分兩串沒配對)。
   修:`gatherWebMulti` 改用 **`parseFindingsWithUrls`**——prompt 要求每條句末附來源網址→逐條抽 url 配對;
   抽不到再用該次 call 的 citations 回填。回傳 `items:[{text,url}]`。`collectSignalItems` 用 it.url →
   scout 引用 #N 對到真連結。`buildSynthPrompt`/sig.web 改吃物件。
3. **Polymarket 等中央源消失** ← render 無誤(有資料才顯示),是該次中央抓取真的回空。加 `[central]` log
   (markets/news/wiki/bluesky/trends 件數 + 各 settled 狀態)→ 下次能判斷是 transient 還是 filter。
4. **深度研究 20 分逾時掛掉** → 上限 20→**40 分**(docs 允許 60);每次 poll **log status**;
   完成狀態寬容判定(completed/succeeded/done);**連續 8 次 poll 失敗就明確報錯**(避免 poll 壞掉偽裝成慢);
   log created id/keys。⚠️ 仍需實機看 console 的 `[deep-research] status=...` 才能確認是真慢還是 poll/狀態名問題。

**注意部署**:使用者該次測的是上一版(reddit 403 還在),最新(含社群查詢+本輪修正)要等 GitHub Pages 部署。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第八輪 / 淺搜廣度:多查詢 Claude web search）

**一句話**:使用者要淺搜也有「~100 條相關資訊」,且明確要用 **Claude 真的上網搜**(不是 Brave/GDELT)。
把 `gatherWeb`(1 次)擴成 **`gatherWebMulti`** —— 跨多組查詢(keyword+entities+各 scout queries,上限 7)、
並行限流 2、聚合去重 → 最多 100 findings + 120 sources。已上 main。
(⚠️ 我一度要去做 Brave/GDELT,使用者澄清「我說的是 Claude 真的上網搜」→ 收回,沒做 Brave/GDELT。)

**第八輪改了什麼(index.html)**:
- `gatherWebMulti(keyword, entities)`:由 keyword + entities + `activeScouts[].queries` 組查詢(去重、≤7),
  concurrency 2 各跑一次 `callClaude({webSearch:true, maxUses:5})`(每次要 12–20 條),聚合去重 findings/sources。
- `runPrediction` 的 gather 改呼叫 `gatherWebMulti`;狀態列顯示「蒐集到 N 條發現 · M 個來源」。
- `collectSignalItems`:web findings 取前 60、webSrc 取前 40 進 scout digest(控 prompt 大小);scout 仍 #N 引用真 URL。
- `buildSynthPrompt`:新增「網路研究發現」block(前 40 條)→ 綜合也直接看到 raw web intel。
- `renderForecast`:🔎 查證來源顯示上限 10→20。
- 舊 `gatherWeb`(單次)已被 `gatherWebMulti` 取代(呼叫點已換)。

**權衡(已知)**:淺搜現在會跑最多 7 次 Claude web search(concurrency 2)→ **較慢(~1–2 分)、較貴(~$0.1–0.3/次)**,
這是廣度的代價。低 Anthropic tier 可能 429 等待變慢(callClaude 有 5 次退避,不會失敗只會慢)。要更快可減 queries 上限。

**驗證重點**:淺搜(web search 開)→ 狀態列「蒐集到 N 條…」N 應該數十;scout 卡片有豐富真內容 + 真來源 chips;
結果頁底「🔎 查證來源」最多 20 個真連結。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第七輪 / 一開始就選模式）

**一句話**:使用者要「輸入時就選模式」而非結果頁再點深挖。已加 **⚡淺搜 / 🔬深挖** 兩個入口;
深挖 = 跑一次快速 pass(拿即時錐+中央資料+lastCtx,**略過 Claude gatherWeb**)→ 自動接 `runDeepResearch`
重繪。複用既有流程,低風險。已上 main。

**順帶澄清的事實**:`understandTopic` **本來就是 Claude**(L1993 callClaude),不是 Gemini —— 我之前架構表寫錯。
所以「facilitator 用 Claude」已是現況。Gemini 現在只剩:scout 解讀(可有可無)+ Deep Research。
另:之前那個「Deep Research 成功」是我誤判 —— 使用者沒點,那批扣題內容其實是 **askOracle(Claude)自己 web search** 查到的
(證明 Claude 搜集可靠),`<cite>` 只是格式殘渣(已 stripCites)。

**第七輪改了什麼(index.html)**:
- 輸入區:`⚡ 淺搜預言`(form submit / Enter)+ 新 `#deepBtn`「🔬 深挖預言」(其下 .mode-row/.mode-deep-btn CSS)。
- `runPrediction(keyword, { gather = true })`:gather=false 時略過 gatherWeb。
- 新 `runDeepPrediction(keyword)`:需 Gemini key;`await runPrediction(kw,{gather:false})` → 若到結果頁則 `runDeepResearch()`。
- BYOK 狀態文更新成「Claude 蒐集+綜合,Gemini 深挖」。
- 架構表(正確版):**Claude = facilitator(understandTopic)+ 淺搜蒐集(gatherWeb web search)+ 綜合(askOracle)**;
  **Gemini = 深挖蒐集(Deep Research agent,唯一真會搜的 Gemini 路徑)**。Gemini 快速 grounding 已證實壞、不用。

**驗證重點**:① 首頁有兩顆鈕;⚡淺搜=快;🔬深挖=先出即時錐再自動跑 Deep Research、跑完重繪錐+真引用、無 cite 亂碼。
② 深挖按鈕沒 Gemini key 會提示。⚠️ 深挖會先跑一次淺 pass(~15s)再進 Deep Research(數分鐘/$1–3)。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第六輪 / 找回真資料 + 清 cite 亂碼）

**一句話**:① Deep Research 餵進錐後 `<cite index=...>` 標籤當亂碼噴出 → 清掉。
② scout 對薄資料題目全空(因為我把 scout 上網拔了)→ **用「單一 Claude web search 蒐集器」找回真資料**
(Claude 的 web_search 真的會搜、回真 citations,跟 Gemini 不一樣;只 1 次呼叫,不會 5x 429)。已上 main。

**第六輪改了什麼(index.html / api)**:
- **cite 亂碼**:`stripCites()`(去 `<cite…>`/`</cite>` 留內文)+ `sanitizeCites()`(遞迴清 result)。
  套在:`markdownToHtml`(報告面板)、`feedDeepResearchIntoCone`(餵 Claude 前 `stripCites(md)` + 輸出 `sanitizeCites`)。
- **找回真資料**:新增 `gatherWeb(keyword, entities)` —— 1 次 `callClaude({webSearch:true, maxUses:6})`,
  回 `{findings, sources}`(真 citations)。`runPrediction` 深掃且 webSearch 開時,先跑 gatherWeb →
  `sig.web`(發現)+`sig.webSrc`(來源);`collectSignalItems` 把這兩者排在最前(scout 有真料可解讀、可 #N 引用真 URL);
  gatherWeb 的 sources 併進最終「🔎 查證來源」。
- **上一輪修的**(也在 main):GDELT 504 regression(改 timeout-safe、總是回 200+JSON+CORS)、`api/bluesky.js` 代理。
- **架構現況**:Gemini 只用在 understandTopic(無搜尋)+ Deep Research agent(Interactions API,會真搜)。
  **scout 蒐集回到 Claude web search**(單一 gatherer)。即時掃 = 中央 API + 1 次 Claude 搜;深掃報告 = Deep Research。

**驗證重點**:① 未來錐/報告不再有 `<cite…>` 字樣 ② 即時深掃(webSearch 開)scout 卡片**有真內容 + 真來源 chips**
③ 結果頁底「🔎 查證來源」有真實可點連結。⚠️ gatherWeb 是 1 次 Claude 搜,會增加數秒延遲與少量費用;
webSearch 關掉就退回「只解讀中央 API 資料」(薄題目會空,正常)。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第五輪 / Stage 2:Deep Research 餵進未來錐）

**一句話**:做完 Stage 2 —— **Deep Research(Interactions API,會真搜、有真引用)跑完後,把報告 + 引用
餵進同一個 `askOracle` 重繪未來錐**,引用變可點來源。已合進 main。

**為什麼**:使用者貼了官方文件,關鍵句「**You cannot access [Deep Research] through `generate_content`**」——
證實 scout 的 `generateContent`+`google_search` 跟 Deep Research 是兩套機制,前者模型自由裁量(會幻覺)、
後者 agent 一定搜。使用者要把「會真搜」的 Deep Research 接成資料源。這正是北極星「兩模式只差搜集、分析相同」。

**第五輪改了什麼(index.html)**:
- `render()` 拆出 **`renderForecast(data, sources)`**(topic/summary/drivers/horizons/cone/wildcard/引用),
  讓 Deep Research 能只重繪錐、不動證據卡與 DR 面板。claudeSources 渲染移進 renderForecast。
- `runPrediction` 存 **`lastCtx = {keyword, sig, expert}`**,供 Deep Research 重用同一分析上下文。
- `buildSynthPrompt` / `askOracle` 新增 **`deepReport`** 參數:有報告時當「主要依據」塞進 prompt 最前。
- 新增 **`extractReportSources(md)`**(抽 markdown 連結 + 裸 URL 去重)、**`feedDeepResearchIntoCone(md)`**。
- `runDeepResearch` 完成時:`renderDeepResearchReport(md)` 後呼叫 `feedDeepResearchIntoCone(md)` → 用
  `askOracle(keyword, lastCtx.sig, [], expert, md)` 重繪未來錐 + 顯示報告引用為來源。失敗則靜默(錐維持原狀)。
- DR CTA 文案加註「並用真實來源重繪未來錐」。

**驗證重點(需實機,Deep Research 每次 $1–3、數分鐘)**:先跑即時深掃 → 結果頁點「🔬 深度研究」→
等它跑完 → ① 上方未來錐應**重繪**(換成基於報告的事件)② 「🔎 查證來源」應出現**真實可點 URL**(來自報告引用)
③ 報告本身仍顯示在下方。若 `lastCtx` 為空(沒先跑預言)則只出報告、不重繪。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第四輪 / 重大轉向）

**一句話**:**徹底放棄 Gemini grounding**(實證它「成功回應卻從不真的搜尋、只幻覺」),把 scout
改成**只解讀我們真抓到的資料(markets/news/reddit/bluesky/trends/wiki)、按編號引用、映射回真 URL**。
push 到 `claude/notes-handoff-review-UXYuR`(PR #1)。**使用者一直在舊正式站(main)測,看不到這些修正。**

**為什麼轉向(鐵證)**:使用者多把 key、多次實測 + 看 Gemini API console:
- console 顯示**請求成功(100% success、有燒 token)**,但結果只有 1 筆無關幻覺。
- raw reply 出現「在取得3比1領先後遭費城76人逆轉淘汰(Wikipedia)」這種**跟主題無關的記憶幻覺 + 假引用**,
  還漏出內心獨白「Let's do this. It satisfies both! …valid JSON」。
- `groundingMetadata = {}` 每次都空 = `google_search` 工具從沒觸發。
→ **結論**:Gemini 的 `google_search` 是「模型自己決定要不要搜」的,**無法強制**,這個 model 選擇幻覺。
  「叫 LLM 請搜尋」這條路死了。**改用真資料 + 真 API 才有真來源。**

**第四輪改了什麼(index.html)**:
- `callGemini`:`bulletGuard` 改成只要 `!responseSchema` 就套(no-search 也要防 CoT 漏);**移除** `!webSearch→JSON mime`
  那段(它會逼出 JSON / 內心獨白)。callGemini 現在**只有 scout 在用**(understandTopic/askOracle 走 Claude)。
- `signalDigest` → `collectSignalItems(sig)` + `buildSignalDigest(items)`:把所有真資料攤成**編號清單 + 真 URL**。
- `scoutPrompts`:改成「**只准用下面編號資料、每條句末標 (#N)、嚴禁記憶/臆測/編造來源**」。
- `runScoutOnce`:**不搜尋**(webSearch:false),吃 digest;解析 bullets 後抓 `#N` 映射回 `items[N].url` → 真 sources。
- `runScout`:**拔掉所有 google_search 分支**,只剩 gemini(解讀)→ claude 降級。`isGeminiOverload`/搜尋重試全刪。
- `api/gdelt.js`:429 退避重試(GDELT 限流 Vercel IP);`fetchGdelt` 留 15 則(給 scout 更多可引用真新聞)。
- 前一輪已修:Kalshi combo 垃圾盤過濾(`isCombo`)、Reddit/Bluesky/Trends 接入、`api/trends.js`。
- 死碼(無害):`SCOUT_SCHEMA`、`GEMINI_MODEL_FALLBACK`、`buzz/github/stackBlock`、`getWebSearch` 現只供最終 askOracle 的 Claude 查證用。

**⚠️ 卡關點:使用者測的是 main(正式站),不是 branch**。行號/行為全是舊 code。要嘛 merge 進 main(需使用者同意,
任務規定不可擅自動 main),要嘛使用者改開 branch preview。且使用者開著 **solo-debug(只跑 1 個 scout)**,要關掉才看得到 5 隊。

**⏳ 下一個 session / 驗證重點**:深掃後 scout 卡片應該:① 不再幻覺、不漏內心獨白 ② findings 句末有 (#N)
③ 底部「探索來源」chips 是真 URL(來自 Polymarket/GDELT/Reddit 等)。Polymarket「馬刺奪冠 64%」那條是真的、可點。
**若仍想要「上百上千來源」的廣度** → 還是得加真搜尋 API(Brave 免費 key,使用者尚未決定)。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第三輪）

**一句話**:修完 scout 四個 bug 後,又**把退役的 Reddit/Bluesky 重新接成 Tier-1 直連硬訊號、
新增 Google Trends proxy**,三者都進 `sig` + `buildSynthPrompt`(分析師現在會吃到)+ 結果頁卡片。
全部 push 到 `claude/notes-handoff-review-UXYuR`(PR #1),**等使用者實機驗證**。

**這輪(訊號源)改了什麼**:
- 使用者問「social signals(X/Threads/Reddit)、Google/TikTok trends 能加嗎?分析師有吃進全部嗎?」
  → 查證:`buildSynthPrompt` 結構上**確實**把 scout findings + 4 個 Tier-1 源全餵給 askOracle(分析師沒漏),
  但**輸入太薄**:grounding 壞 + Reddit/Bluesky/HN…全被 V2 退役沒接。X/Threads/TikTok 純前端拿不到(付費/門禁)。
- 使用者選:**重接 Reddit + Bluesky + 加 Google Trends,直接動手**。
- 做法:`runPrediction` 的抓取改 `Promise.allSettled`,加 `fetchReddit/fetchBluesky/fetchTrends`,
  進 `sig.reddit/bluesky/trends`;`buildSynthPrompt` 加「社群即時聲量 Reddit/Bluesky」+「搜尋熱度 Google Trends」區塊;
  結果頁加 `socialCard`(Reddit+Bluesky 合併、可點)+ `trendsCard`(sparkline)。`buzzCard`(HN)正式退場。
- **Google Trends**:無官方 API + CORS,所以走**新的 `api/trends.js` proxy**(explore→multiline 二段 token flow,
  伺服端做)。**只在有設代理時生效**(使用者已設 oracle-bice.vercel.app);push 後 Vercel 自動部署這支新 function。
  ⚠️ 非官方端點、Google 會限流 → 失敗一律回 series:[] 優雅降級。Bluesky 免代理就 CORS-OK;Reddit 走既有 /api/reddit。
- **X/Threads/TikTok**:純前端搆不到,沒做(X 用 Bluesky 替身)。

**第二輪(scout bug)摘要**(仍待驗證):`jsonGuard`→`bulletGuard` 解除 JSON 強制(grounding 元兇)、
findings 3–5→10–15、cap 6→20、maxTokens 1500→4096、GDELT 加 `sourcelang:eng`+關聯度過濾。

**⏳ 下一個 session 第一件事:實機驗證(hard refresh + 深掃 + Gemini key + 確認代理已設)**:
1. scout 卡片亂碼消失? Console `M sources > 0`? findings 變多?(第二輪的核心待驗點)
2. 結果頁有沒有冒出 **社群卡(Reddit+Bluesky)**、**Google Trends sparkline**?GDELT 是英文相關?
3. Console 有沒有 `/api/trends` 的成功回應(proxy 部署 + 非官方端點是否還通)?
→ 若 Trends 一直空 = Google 擋了非官方端點 or proxy 沒部署成功,要看 Vercel function log。

**實機看到的症狀(使用者截圖)**:① scout 卡片冒出亂碼 `"findings": [` ② sources 是德語肥皂劇番組表
(rtl.de GZSZ/AWZ)根本讀不了 ③「主流前沿」只有 2 條,太少、沒 research rigor ④ Console:
`groundingMetadata = {}` / `finishReason = STOP` / `0 sources`,raw reply 還是 `{"findings":[…]}`。

**真因(已用程式碼裏實)**:
- **0 sources 的元兇 = 我們自己用 prompt 把 grounding 殺了**。`callGemini` 的 `jsonGuard`
  (原 L1805)在 `webSearch && !responseSchema`(=scout 採集)時硬塞「回覆必須是 `{`…`}` 的純 JSON」。
  Gemini 被命令吐 JSON → 不呼叫 google_search、改用記憶直答 → groundingMetadata 空。V2 拆掉 schema 了,
  但這把 **prompt 版的 JSON 強制**還留著,等於白拆。
- **亂碼 `"findings": [` = 同一根因的副作用**。Gemini 折衷成 `{"findings":["- …"]}`,`parseFindings`
  認不出被引號包住的 bullet → fallback 撈進 JSON 骨架當「發現」。
- **德語 sources** = `gdeltOnce` 只做全文比對,**無語言/相關度過濾**(HN 有 maxRelevance,GDELT 沒有)。

**這輪改了(index.html,4 處)**:
1. `jsonGuard` → **`bulletGuard`**:webSearch 採集時**不再強制 JSON**,改要「只輸出 `- ` 開頭條列、
   絕不要大括號/JSON」。這是讓 grounding 真正開火的關鍵改動。
2. `scoutPrompts`:「3–5 條」→「**至少 10–15 條**、多搜幾輪、覆蓋多面向、要有研究嚴謹度」。
3. `parseFindings` 上限 6→**20**,並濾掉殘留的 `"findings":` / 裸括號;scout `maxTokens` 1500→**4096**
   (Gemini 3 thinking 會吃掉輸出預算,1500 把 findings 餓到只剩 2)。
4. `gdeltOnce` 加 **`sourcelang:eng`** + `fetchGdelt` 加 `maxRelevance>=2` 過濾,內部抓量 8→25/30。

**⏳ 下一個 session 第一件事:再請使用者實機驗證(hard refresh + 深掃 + Gemini key)**:
1. scout 卡片**還有沒有亂碼**(`"findings": [`)→ 應該消失
2. Console `✓ gemini+search → N findings, M sources` 的 **M 有沒有 > 0**(這是成敗關鍵)
3. findings 是不是變多(10+)、GDELT 新聞是不是英文且相關
→ **若 M 仍是 0** = 連不強制 JSON 都不 ground,那 gemini-3.5-flash 瀏覽器直連可能根本不回 grounding,
  要改走別招(換 model / 改用 Deep Research 那條 / 或前端不靠 Gemini grounding 改靠 Claude web search)。

---

## 🪧 交接便條（給下一個 session 的你 — 2026-06-01 · 第一輪）

**一句話**：剛完成 **V2 Stage 1 重構**（Gemini 搜集 + Claude 分析），已 push（`origin/main` = `0347b03`），
**等使用者實機驗證**。使用者開新視窗是因為 context 快滿，工作本身沒中斷。

**北極星（使用者定的目的）**：找最新/最相關/emerging+strong 且**有可點來源**的信號 → 同一個分析引擎推演未來 18 個月。
兩模式只差「搜集」：**即時淺掃**=快廣淺（近 7 天）、**深度研究**=慢廣深（大趨勢）；分析完全相同。

**V2 核心轉向**：`responseSchema` 會靜默禁用 Gemini grounding（所以 sources 一直空）→ 拆成
**Gemini 當搜集器（不上 schema、回 bullets+sources）+ Claude 當分析器（JSON 綜合）**。

**⏳ 第一件事：請使用者實機驗證 Stage 1**（hard refresh + 深掃 + Gemini key）：
1. scout 卡片底部**有沒有「探索來源」chips 且可點**（這是這次最關鍵的修復）
2. Console 有沒有 `✓ gemini+search → N findings, M sources`，且 **M > 0**
3. 不再出現「無法解析的格式」
→ 若 sources 出來了 = 核心架構成立,可進 Stage 2。若 M 還是 0 = Gemini 無 schema 仍不回 grounding,要再想辦法。

**📋 Stage 2 待辦（還沒做）**：
- Google Trends 代理（量化搜尋熱度曲線,Tier-1 硬數據;走 Vercel proxy,標實驗性）
- 把「深度研究」報告也餵進**同一個 askOracle 分析引擎**（目前深研只渲染報告,還沒接進未來錐）
- 清死碼：`signalDigest`、`SCOUT_SCHEMA`、退役的 `*Block` 與 `fetchHN/GitHub/StackEx/Bluesky/Reddit`

**🔧 環境提醒**：
- 網站 URL：`https://jasperwu.github.io/oracle/`；Vercel 代理：`oracle-bice.vercel.app`（已設在前端設定）
- 沙箱**連不了外網** → 所有 API 行為都要靠使用者實機截圖驗證
- 安全網：`backup/pre-v2-refactor` @ `615e4d4`（V2 重構前）、`backup/pre-gemini-integration` @ `0ff5279`
- Gemini 預設 model `gemini-3.5-flash`（使用者指定）;深掃/快速由「多代理人 fringe 深掃」開關控制（無獨立「快速模式」鈕）

---

## 2026-06-01 · V2 重構 Stage 1：Gemini 搜集 + Claude 分析（核心架構轉向）

**北極星（使用者定）**：找最新/最相關/emerging+strong 且**有來源**的信號 → 同一個分析引擎推演未來。
**兩模式只差在「搜集」，分析完全相同。** 即時淺掃=快廣淺（近 7 天）；深度研究=慢廣深（大趨勢）。

**根本轉向**：`responseSchema` 會**靜默禁用 Gemini grounding**（sources 永遠空）。所以拆乾淨：
- **Gemini = 搜集器**（grounded search、**不上 schema** → 一定有 source URLs），回**條列 bullets + sources**（不要 JSON）。
- **Claude = 分析器**（understandTopic + askOracle 綜合 → 未來錐 JSON）。低頻 → 不撞 429。

**Stage 1 已改（這次）**：
- `scoutPrompts`：改成「情報蒐集」prompt，要 3–5 條 bullet、**聚焦最近 7 天**、句末標來源；不再要 JSON/schema。
- `runScoutOnce`：Gemini 無 schema grounded → `parseFindings()` 抽 bullets → 回 `{findings, sources}`。
- `runScout`：回傳 `{scout, findings, sources, error, degraded, provider}`；fallback 鏈簡化
  （gemini+search → gemini-fb model → claude no-search rescue）。
- `buildSynthPrompt`：scoutBlock 改餵 findings + 各 scout 的來源網域；**退役** buzz/github/stack/bluesky/reddit 區塊。
- `renderScoutFindings`：scout 卡片改顯示 bullets + 「探索來源」chips（不再有邊緣度 bar）。
- `runPrediction`：Tier-1 只抓 Polymarket+Kalshi+GDELT+Wikipedia；**移除** HN/GitHub/Stack/Bluesky/Reddit 直連。
- render：移除 HN(buzz) 卡片。
- 死碼（無害、暫留）：`signalDigest`、`SCOUT_SCHEMA`、各退役 `*Block`、`fetchHN/GitHub/StackEx/Bluesky/Reddit`。

**安全網**：`backup/pre-v2-refactor` @ `615e4d4`（遠端）。
**Stage 2（未做）**：Google Trends 代理（量化搜尋熱度）+ 把 Deep Research 報告也餵進同一分析引擎。
**未驗證**：沙箱無法測；需實機確認 Gemini 無 schema 是否真的回 grounding sources（理論上會）。

---

## 2026-06-01 · 加「深度研究」按鈕（Gemini Deep Research Agent · 選項 B）

**背景**：Gemini `generateContent` + `responseSchema` 會**靜默禁用 grounding**（gm keys=Array(0)），
所以即時 scout 永遠拿不到可點 sources。使用者發現 Google 的 **Deep Research Agent**（Interactions API）。
讀完官方文件確認：**非同步**（`background=true` + 輪詢）、**無 structured output**（回 markdown 報告）、
**每次 $1–7 美元、3–20 分鐘**、有完整引用。→ 不適合當即時主路徑，但**很適合當結果頁上的「深度研究」按鈕**。

**決策（使用者選 B）**：即時未來錐維持不變，**結果頁加一個選用的「深度研究」CTA**：
點下去才啟動一個背景 Deep Research 任務、輪詢、渲染有引用的報告。**完全 additive，不動 scout 流程。**

**實作**：
- 端點常數 `GEMINI_INTERACTIONS`、`DEEP_RESEARCH_AGENT='deep-research-preview-04-2026'`、`GEMINI_API_REVISION`。
- `runDeepResearch()`：POST 建立 interaction（`background:true, store:true, agent_config.thinking_summaries:auto`）
  → 每 10s 輪詢 → `status==='completed'` 取 `output_text` → `markdownToHtml()` 渲染；有取消鈕、計時、最新 thought 顯示。
- 用 `drCurrentTopic`（render 前由 keyword 設定）當研究主題；`resetDeepResearchPanel()` 每次新預言時重置。
- `markdownToHtml()`：自寫的安全 markdown 渲染（escape→標題/粗體/連結/清單/**表格**），Node 實測 OK。
- **CORS**：新增 `api/interactions.js` proxy（POST 建立 + GET 輪詢，轉送 `x-goog-api-key`）。前端 `proxied('/api/interactions')`
  有設代理走代理、否則直連。使用者已有 Vercel 代理 → git push 會 auto-deploy 這支新 function。
- UI：`.deep-research` 面板（CTA→進度→報告三態）+ 費用/時間警語。

**待驗證（沙箱無法測）**：① Interactions API 能否瀏覽器直連 or 一定要 proxy ② 該預覽功能是否對 Tier 1 金鑰開放
③ 回應 `id`/`status`/`output_text`/`steps` 的真實欄位名。失敗會顯示明確錯誤，不影響即時預言。

---

## 2026-06-01 · 後端代理:Vercel serverless 解 CORS（路線 1）

**背景**:GDELT 過去穩定，最近被 CORS 擋（GDELT 服務端政策改變，跟 git 歷史比對證實
程式碼從未動過）。Kalshi 同；Reddit 也擋。使用者拍板**路線 1**：自建後端代理。

**架構（首次打破「純前端」原則）**:
- `api/gdelt.js`、`api/kalshi.js`、`api/reddit.js` 三支 Vercel serverless function。
  接收前端的 query string，從 server 端打第三方，回 CORS-open 的 JSON（含短快取）。
- `vercel.json`（functions config，maxDuration 10s）+ `package.json`（type:module）。
- 前端 modal 加「**自有後端 URL（可選）**」欄位 → `LS_PROXY_BASE` → `getProxyBase()` /
  `proxied(path)` helper。
- `gdeltOnce`、`fetchKalshi`、`fetchReddit` 三處改成：**有設代理就走代理，沒設就走原本**。
  完全 backward-compatible，使用者不設也不會壞，只是 CORS 還會卡。
- BYOK 狀態列尾加「· 後端代理已啟用」可視化提示。

**部署**:寫了 `DEPLOY.md`（3 步驟：Vercel 用 GitHub 登入 → Import repo → 貼 URL 回設定）。

**已知限制**:
- Vercel 免費 tier 有 10s function timeout（vercel.json 已寫死保護）。
- Reddit 我們依然要遵守它的 robots/UA 規範（UA 已設為 `foresight-oracle/1.0`）。
- Polymarket 不走代理（它本來就 CORS-OK）。
- 沙箱無法實測 serverless，需使用者部署後實機驗證。

---

## 2026-05-30 · Gemini 整合 Phase 1:scout 用 Gemini、綜合用 Claude

**目的**:解掉「離線判讀」根因——5 scout 並行 web search 撞 Anthropic 30k/min 429。
**架構**:scout 收集走 Gemini(自家 google_search grounding、免費 tier 寬鬆),
askOracle 綜合維持 Claude(深度推理)。**兩把獨立 key,獨立計費,互不撞牆。**

**備份**:`backup/pre-gemini-integration` @ `0ff5279` 已推 origin。Tag `v1-pre-gemini`
本地有,遠端 push 因網路一直失敗,但分支即足夠安全網。

**做了**(Phase 1):
- UI:modal 加第二個輸入框(Anthropic / Gemini 兩把,各自存 localStorage、各自能清),
  `refreshByokNote` 改顯示「兩把都就緒 / 只有一把 / 都沒設」三態。
- 端點常數:`GEMINI_MODEL = 'gemini-2.5-flash'`、`GEMINI_URL(key)`。
- 新函式 `callGemini(system, user, {webSearch, maxTokens, timeoutMs})`:
  - 請求格式 `{systemInstruction, contents, tools:[{google_search:{}}]}`、
    `generationConfig.responseMimeType:'application/json'` 強制 JSON 輸出。
  - 回應:抽 `candidates[0].content.parts[].text`;sources 從
    `candidates[0].groundingMetadata.groundingChunks[].web.{uri,title}` 取。
  - 同 callClaude:AbortController timeout、429/503 退避重試(讀 retry-after)、
    走 `onClaudeWait` hook 把等待秒數秀到 UI。
- `runScoutOnce` 多一個 `provider` 參數;`runScout` 三段式 fallback:
  primary(有 Gemini key → gemini,否則 claude) → primary 去掉 web search →
  若 primary 是 gemini 還掛,**最後 fallback 到 claude 無 web search**。
  回傳多帶 `provider` 旗標方便日後追蹤/UI 顯示。
- askOracle 不動(維持 Claude)。

**還沒做**(Phase 2):
- 結果頁卡片顯示「此 scout 由 Gemini/Claude 提供」(目前只在 result 物件裡有 `provider`)。
- Gemini JSON 輸出若不夠聽話的話,微調 prompt。
- 實機驗證:沙箱擋外網,無法測 Gemini 端點真實行為(JSON 格式、grounding chunks 結構),
  使用者實機跑時若解析失敗會走 fallback 鏈,最差也只回到舊行為。

---

## 2026-05-29 · 試接 Reddit(方案 A:純前端直連)

**背景**:使用者過去專案會抓 Reddit/subreddit 的 emerging signals,問我們有沒有做。
**釐清**:之前**沒有** Reddit 管道——社群類只有 Hacker News(科技)+ Bluesky;web search 偶爾
可能瞄到 Reddit 連結摘要,但非針對性。Reddit 是 niche/早期訊號金礦,niche scout 缺的拼圖。
**決策(使用者選 A)**:先試**純前端直連** `www.reddit.com/search.json`(零成本)。
**實作**:`fetchReddit`(sort=relevance、t=month、limit 20 → `maxRelevance≥5` 過濾 →
依留言數/分數排序取 6),`redditBlock` 進 `signalDigest` + 綜合 prompt;`sig` 多 `reddit`。
**風險(關鍵)**:⚠️ Reddit 常擋瀏覽器直連(CORS/限流),沙箱無法驗證——**很可能回空**。
失敗 graceful 回 []、不影響其他來源。若實機證實被擋,選項 B 是等後端代理階段再接。
**結果頁**:同 GitHub/Stack/Bluesky,Reddit 也**尚無顯示卡片**,只進分析。

## 2026-05-29 · 優化搜尋品質與分析角度(1+2+3+4)

在「廣度淺掃」框架內提升品質,使用者選做四項:
1. **時效 query**:scout 的 web search 強制偏向「最近 6 個月 / 2026 / latest / upcoming」。
2. **預擬 query 分散**:`understandTopic` 為每個 scout 預先擬 2–3 條「彼此不重複、鎖定各自角度」
   的具體查詢(`scout.queries`),從源頭避免 5 位查到同一批結果。scoutPrompts 把這些 query
   列進 web search 指示;沒有就 fallback 到 keyword+entities。
3. **entities 餵進 scout**:`entities` 一路 thread 到 `scoutPrompts`(runScouts→runScout→
   runScoutOnce→scoutPrompts),scout 的搜尋與判讀都用得上展開後的實體。
4. **signal 加時間維度**:每條 signal 新增 `timing`(now/emerging/distant)與
   `momentum`(accelerating/steady/fading);`buildSynthPrompt` 把這兩個標籤帶進綜合,
   讓事件更準地對到 horizon。
**未動**:呼叫次數/速度不變(只改 prompt 與既有資料的傳遞)。fringe→錐圖、stance 平衡照舊。

---

## 2026-05-29 · 架構認知:我們是「廣度淺掃」,非 Claude Research 式深研

**使用者問**:我們的 web search 跟 claude.ai 的 Research 一樣嗎?也是讀上百網站選 signals 嗎?
**釐清(重要認知)**:
- **我們網站** = **單次** API 呼叫 + `web_search` 工具(每 scout `max_uses:3`)。一次呼叫裡搜幾次、
  讀的是**搜尋結果摘要**(非全文),就得在同一次回應交出 signals。整場深掃最多 ~19 次搜尋
  ≈ 掃過一兩百筆**摘要**(淺層)。signals 6 條是**每個 scout** 上限,非從上百筆精選。
- **Claude Research** = **多步驟 agentic 回圈**:搜→讀全文→發現缺口→再搜→再讀,反覆多輪,
  真的造訪上百網站、自訂研究計畫,故意花數分鐘做深度。
- **差別本質是架構**(單次 vs 多輪 agent),不是調參數能補。我們的「慢」買到的是**廣度淺掃**,
  非深度研究。

**使用者定案**:**認同廣度淺掃** —— 它能給更快、更好互動的預測 demo。
下一步聚焦：**優化「搜尋品質」與「分析角度」**(不轉成多輪深研)。深度升級(scout→多輪 agent)
列為未來大方向，晚點再決定。

---

## 2026-05-29 · 綜合步驟卡很久 → 加逾時 + 退避回饋

**現象(fandom K-pop)**：scout 已 5/5 回報,卡在「綜合所有訊號，推演未來…」很久,像當機。
**根因**：`askOracle` 是**單一大呼叫**(maxTokens 4500 + web search ≤4)本就慢;若撞 429,
`callClaude` **靜默退避**最多 30s×5≈2 分鐘,且 **fetch 沒 timeout、退避時無任何畫面回饋**。

**修法**：
1. `callClaude` 加 **AbortController**，單次 fetch 逾時(timeoutMs 預設 90s)就 abort→重試，
   重試上限後拋「連線逾時」，不再無限等。
2. 退避時呼叫 **`onClaudeWait(secs)`** hook；`runPrediction` 在綜合階段接上它，
   畫面 sub 文字顯示「遇到流量限制，N 秒後重試…」，讓等待可見而非看似凍結。

**仍未解的根**：速度本身——5 scout 各自 web search + 4500-token 綜合，量大。要更快仍需
減少 web search 量或升 tier（持續記為待辦）。

---

## 2026-05-29 · 選擇標準:動態混編 stance + fringe 接進未來錐

**使用者洞察**:選擇標準該 balance —— 強訊號=最可能發生→靠近錐**中心**；越 niche→錐**外圍**。
且**抓取階段就要 balance**，不能只修最後顯示。
**診斷**:① 抓取層 8 來源全偏 hot（成交量/star/活躍度/互動排序），niche 在源頭就被濾掉；
② scout prompt 說「主流也行邊緣也行」=沒標準；③ 錐圖 Y 只看 `likelihood`，scout 的 `fringe`
**只顯示在卡片進度條、完全沒進錐圖**——中心/外圍的隱喻是假的。

**決策**:**動態混編**（非固定配額）。
**實作**:
1. **stance**：`understandTopic` 為每個 scout 指派 `stance`（hot/niche/mixed），prompt 要求整隊平衡
   （約 2 hot / 2 niche / 1 mixed）；模型沒給就用 `STANCE_SLOTS` fallback。`DEFAULT_SCOUTS` 也帶 stance。
2. **抓取分工**：`STANCE_BRIEF` 依 stance 改寫每個 scout 的 system/task/fringe 指示——
   hot 聚焦主流確定（fringe 0–35）、niche 專挖冷門早期（fringe 55–95）、mixed 兼顧。
   這就是「抓取階段的 balance」：有人負責中心、有人負責外圍。
3. **fringe 進錐圖**：綜合 agent 的每個 event 也輸出 `fringe`；`plotCone` 的 Y 改成
   `LIK_FRAC[lk]*0.45 + fringeFrac*0.55`——主流高確定→中心軸，niche 冷門→外圍。缺 fringe 退回只看 likelihood。
   Node 實測:probable+fringe5→0.14(中心)、possible+fringe90→0.86(外圍)。

**取捨**:stance 分工讓 niche scout 更依賴 web search 挖長尾（hot/star 類 API 本質是熱度榜，
抓不到未紅的東西）→ web search 量仍是成本/429 風險。

---

## 2026-05-29 · scout 訊號上限 4 → 6

**現象(fandom and K-pop,動態組隊讚:飯圈觀察/平台偵探/商業解碼/認同探員/黑暗面鏡)**：
使用者問每個 scout 為何最多只有 4 個訊號。
**根因**：雙重寫死——prompt「給 2–4 個訊號」(L1513) + 程式 `slice(0,4)`(L1522)。
**修法**：放寬到 6（prompt「3–6 個」+ `slice(0,6)`）。**取捨**：訊號多→token 多、回應長、
較易截斷/撞 429、深掃更慢；6 是豐富度與穩定的折衷。`extractJSON` 截斷搶救仍是後盾。

---

## 2026-05-29 · 回退 Polymarket search(造成兩個 regression)

**現象(travel × AI)**:① 市場出現無關 MLB ② 市場卡片**不能點**(之前可以)。
**根因(同源)**:先前加的「search 優先」`fetchMarkets` 用 `requireScore:false`(搜尋回什麼全收),
且 Gamma `/public-search` 回傳的市場**結構缺正確 event slug** → `m.url=null` → 結果頁渲染成
不可點的 `<div>`(`m.url ? 'a' : 'div'`)。沙箱擋外網**無法驗證 search 真實格式**,踩雷。

**修法**:**移除 search 路徑**(`searchPolymarket` / `GAMMA_SEARCH` 全刪),`fetchMarkets`
只走**分頁 /markets**(slug/URL 可靠)+ `requireScore:true` 相關性過濾;沒相關就回 []、
結果頁卡片隱藏(`marketSource.hidden`)。Node 實測:MLB 對 travel×AI 評 0 分被擋,
相關市場(AI/Booking)正常顯示且可點。

**已知小取捨**:`AI` 是短又常見詞,純 AI、與旅遊無關的市場可能仍顯示(總比 MLB 好);
若實測太雜再收。Kalshi 維持 cursor 分頁不變。

---

## 2026-05-29 · 結果頁顯示每個 scout 的「探索來源」

**背景(實測「travel industry in AI era」)**:動態組隊漂亮(訂房探員/航空偵察/行程嚮導/
體驗研究/風險觀察),多數 ✓ 有訊號=降級重試生效。使用者問:看得到 scout 去了哪些網站嗎?
**發現**:`runScout` 早就回傳 `sources`(web search 引用網址),但 `renderScoutFindings`
**沒顯示**、直接丟掉。資料在,只是沒露出來。

**修法**:scout 卡片底部加「探索來源」chips —— `scoutSourcesHTML` 取 `r.sources`、
`hostOf` 抽網域、去重、最多 6 個,可點擊開原文。順帶:若該 scout 是**降級**(degraded,
未用 web search)在卡片標題加「離線判讀」小標,讓使用者知道那張卡沒有即時來源。

**仍待觀察**:速度（使用者覺得有點花時間）——5 scout 各自 web search 仍是主成本，
#3（減少 web search 量 / 升 tier）尚未做。

---

## 2026-05-29 · 區分「出錯 vs 無訊號」+ scout 失敗自動降級重試

**問題**:開了 web search 卻「無訊號」不合理——網路搜尋一定有東西。診斷出 `runScout` 的
`catch` 把**所有失敗**(web search 超時 / 429 / JSON 解析失敗)都靜默變成 `signals:[]`，
UI 顯示「無訊號」與「真的沒資料」**長得一模一樣**,使用者無從分辨。429 因 5 scout 各自
web search 被放大,是最可能元兇。

**修法(使用者選 1+2)**:
1. **區分狀態**:`runScout` 回傳帶 `error` 旗標;`runScouts` 傳 `'error'` 給 `updateScout`；
   UI 新增 `.errored` 樣式,顯示「⚠ 連線失敗」(灰階+陶土紅),不再偽裝成「— 無訊號」。
2. **降級重試**:抽出 `runScoutOnce`;attempt 1 帶 web search,失敗 → attempt 2 **去掉 web search**
   (靠共用資料 + 領域知識作答),兩次都掛才標 error。`degraded` 旗標記錄是否降級。

**效果**:真‧無資料才顯示「無訊號」;壞掉顯示「連線失敗」;大多數情況降級重試後仍有產出。
**未做**:#3 降低 429（減少 scout web search 量）—先觀察 1+2 是否就夠。

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
