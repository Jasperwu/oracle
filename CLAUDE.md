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
2. **深掃轉場 = pixel agent「mission control」監控台**(已完成,見下)。
   照參考圖做成「監控台 / 格子 + 狀態列」,**不是**滿場亂跑的角色 —— 對 talk 更專業也更穩。
3. **結果頁維持原樣,不要動** —— futures cone + horizons 的優雅結果頁是定案的,
   除非明確要求,不要改它。深掃轉場的「反差」正是建立在結果頁的優雅上。
4. **盲做要選可精準掌控的視覺** —— pixel 角色是 grid-of-rects,盲做也不會壞;
   避免徒手畫複雜造型(例如手)那種容易翻車的東西。

## 目前狀態

- **已完成**:多 agent 邊緣訊號掃描 (5 個 scouts) + pixel agent mission-control 深掃轉場。
- **最新 commit**:`Add pixel-art agent mission-control transition (deep scan)`。
- **待辦 / 下一步候選**:context-aware 的 design actions(決策 #1,尚未開工)。

## 程式結構速查 (index.html, 單檔 ~1800 行)

- **5 個 scouts**:定義在 `const SCOUTS`(約 L1238)。
  id: `research` 🔬 / `markets` 📊 / `culture` 💬 / `policy` ⚖️ / `contrarian` 🎲。
- **訊號擷取**:`fetchMarkets`(Polymarket)、`fetchKalshi`、`fetchGdelt`(新聞)、
  `fetchHN`(Hacker News)、`fetchWikiTrend`(Wikipedia pageviews)。
- **Claude 呼叫**:`callClaude()` (L1200) → `runScout()` / `askOracle()`(綜合)。
- **深掃轉場 (mission control)**:`initScoutBoard` / `updateScout` / `creatureSVG`
  (pixel 角色,grid-of-rects SVG) / `startMissionClock` / `stopMissionClock`。
  overlay 加上 `.mission-mode` class 切成深色監控台;`#missionClock` 時鐘、
  `#missionFootCount` 顯示「scouts returned k/5」。
- **結果頁**:`render()` / `plotCone()`(futures cone)/ `initConeScrubber()`(時間軸拖曳)。
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
