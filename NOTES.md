# 對話與決策時間線 (NOTES.md)

> 這份檔案保存我們合作的**脈絡與決策過程**,讓任何新 session 都能無痛接上。
> 規範見 `CLAUDE.md`。**最新的記在最上面。**

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
