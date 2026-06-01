# 部署你的 Vercel 後端代理（3 步驟）

這份指南讓你把 `api/gdelt.js` / `api/kalshi.js` / `api/reddit.js` 三個輕量函式部署上 Vercel，
解掉 GDELT/Kalshi/Reddit 的 CORS 問題。

**不用學程式、不用維護伺服器、不收費**（流量遠在免費額度內）。

---

## 步驟 1 · 登入 Vercel（2 分鐘）

1. 開 https://vercel.com/signup
2. 點「**Continue with GitHub**」
3. 授權 Vercel 讀你的 GitHub repo

---

## 步驟 2 · Import 這個 repo（2 分鐘）

1. 登入後在 Dashboard 點「**Add New → Project**」
2. 找到你的 `oracle` repo，按右邊的「**Import**」
3. **Configure Project** 頁面**什麼都不要改**，直接點「**Deploy**」
   - Framework Preset：Other（自動偵測即可）
   - Build/Output 都留空（這是純前端 + serverless）
4. 等 30–60 秒，看到 🎉 慶祝畫面就完成

---

## 步驟 3 · 把 URL 貼回網站設定（30 秒）

部署成功後 Vercel 會給你一個網址，長這樣：
```
https://oracle-<亂碼>.vercel.app
```

把它**完整貼進**網站「設定金鑰」裡的「**自有後端 URL**」欄位，按「儲存」。

完成後狀態列會顯示「**· 後端代理已啟用**」，GDELT/Kalshi/Reddit 就會自動走代理，永遠不撞 CORS。

---

## 驗證代理有沒有通

打開瀏覽器 DevTools → Network，跑一次深掃，找這三個請求：
- `your-url.vercel.app/api/gdelt?query=...`
- `your-url.vercel.app/api/kalshi?status=open...`
- `your-url.vercel.app/api/reddit?q=...`

應該都是 **200 OK**，回的是 JSON。

---

## 之後的更新

每次你 `git push` 到 `main`，Vercel 會**自動重新部署**。網址不變。

## 想拔掉代理

把「自有後端 URL」清空、儲存即可。網站會立刻退回直接打第三方 API（GDELT/Kalshi/Reddit
可能 CORS 失敗，但不影響其他來源）。
