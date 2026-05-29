# 對話與決策時間線 (NOTES.md)

> 這份檔案保存我們合作的**脈絡與決策過程**,讓任何新 session 都能無痛接上。
> 規範見 `CLAUDE.md`。**最新的記在最上面。**

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
