# 汽車展示教學網站修訂與實測紀錄

檢查日期：2026-10-01（Asia/Taipei）  
依據：`bmw_teaching_plan.md`；修訂檔案：`index.html`。教學計畫維持原內容。

## 修訂內容與原因

- 展開原先擠在同一行的卡片、設計區與表單，統一 HTML 縮排，CSS 色彩集中為變數，JavaScript 使用具名常數。
- 加入精簡註解，說明語意區塊、Bootstrap 斷點、靜態分類、前端驗證與取消提交，方便課堂逐段閱讀。
- 補上「品牌研究與課堂再創作」及對應導覽入口，交代分類 → 比較 → 行動的觀察流程與非官方、虛構資料界線。
- 保留靜態 Hero、三張虛構車款卡及原創幾何圖形；分類用靜態文字，沒有假篩選操作。頁尾補充 CSS／幾何素材來源，未使用官方照片或 Logo。
- 維持 Bootstrap 手機 1 欄、md 2 欄、lg 3 欄格線；手機縮減 Hero 留白，主要操作至少 44px 高。
- 補上按鈕的 hover／active 配色、適用明暗背景的鍵盤焦點，以及卡片連結的個別可讀名稱。減少動態效果設定下不啟用卡片移動。
- 小螢幕導覽連結選取後自動收合，焦點轉移至目的區塊；選單按鈕的 `aria-expanded` 與中文標籤同步。
- 表單改為「虛構稱呼（必填）」、30 字限制與示意輸入提示；使用原生 required 驗證，另外排除純空白稱呼。
- 提交僅以 `preventDefault()` 攔截、驗證、清空欄位及更新 `role="status"` 提示。沒有 fetch、XHR、儲存 API 或個資輸出，也移除欄位的 name 屬性。
- 欄位與提交按鈕預設停用，攔截器掛載後才啟用；停用 JavaScript 時顯示說明並保持停用，防止預設表單提交。

## 實際檢查方法

使用本機 HTTP 伺服器與 Google Chrome 154.0.8037.58 headless，透過 Chrome DevTools Protocol 設定 CSS viewport、送出滑鼠及鍵盤事件、讀取 DOM、監看請求與截圖。不是僅以 CSS 推算結果。三張完整頁面截圖皆已視覺檢視，標題、卡片、表單與頁尾未見裁切或重疊。

測試程式：[qa/check_site.py](qa/check_site.py)；原始量測：[qa/results.json](qa/results.json)。原版備份：[qa/index.before.html](qa/index.before.html)。

## 三種寬度結果

| CSS viewport | 文件 scrollWidth | 車款排列／卡片寬 | 導覽 | 視覺與溢出結果 |
|---|---:|---|---|---|
| 375px | 360px | 1 欄；336px | 折疊；展開、四個連結、收合及焦點轉移通過 | Hero、卡片與表單可讀；無橫向溢出 |
| 768px | 753px | 2 欄，第三張在下一列；336px | 折疊；展開、四個連結、收合及焦點轉移通過 | 兩欄保有間距；表單垂直排列；無橫向溢出 |
| 1440px | 1425px | 3 欄；416px | 桌機導覽四個連結通過 | 卡片同列等高；設計區、表單左右排列；無橫向溢出 |

文件寬比 viewport 少 15px 是本次 Chrome 垂直捲軸占位；判斷條件為 scrollWidth 不大於 viewport。

截圖：[375px](qa/375.png)、[768px](qa/768.png)、[1440px](qa/1440.png)。截圖保留成功提示及輸入欄位焦點；欄位中「同學 A」為清空後顯示的 placeholder。

## 導覽、鍵盤與表單結果

- 三種寬度：所有頁內錨點目標存在，四個導覽入口、Hero 按鈕與三張卡片連結皆可到達目的區塊。
- 三種寬度：Tab 可到「跳到主要內容」，Enter 會將焦點移至 main。
- 額外在 375px 以鍵盤確認：Enter 展開選單、Tab 到研究說明連結、Enter 導覽並收合及移轉焦點；表單 Tab 可依序到分類與送出按鈕。
- 三種寬度皆確認：空稱呼被 required 阻擋、純空白稱呼被自訂驗證阻擋、未選分類被 required 阻擋；修正後 Enter 成功操作，顯示提示並清空兩欄。
- 表單操作期間新增網路請求為 **0**；攔截到的 Storage.setItem 寫入為 **0**；localStorage、sessionStorage 與 cookie 均為空。程式碼檢視亦未發現 IndexedDB、送出資料或儲存資料的呼叫。
- 停用 JavaScript 實測：fieldset 保持 disabled，noscript 說明可見。
- 減少動態效果實測：卡片 transition 為 0s、transform 為 none。
- Chrome JavaScript 執行錯誤：**0**。
- HTML 靜態檢查：標籤巢狀配對與 ID 唯一性通過。

## 色彩與範圍限制

主要固定色彩以 sRGB 相對亮度公式計算：藍色／白色 7.22:1、次要文字／白色 6.38:1、次要文字／淡藍背景 5.78:1、正文／白色 16.46:1；白底焦點外框 6.23:1。這是固定色彩抽查，未將所有漸層位置、瀏覽器狀態逐一做完整 WCAG 稽核。

本次為 Chrome viewport 模擬與鍵盤實測；沒有宣稱已測實體手機、Safari／Firefox 或螢幕閱讀器。原生 select 的選項鍵盤操作未獲本次 CDP 測試驗證（ArrowDown／Enter 模擬未成功改變值），因此僅確認 Tab 可到達分類欄位；分類驗證測試使用 DOM 設定選項。Bootstrap CSS／JS 維持原本 CDN 來源，載入需要網路；CDN 失敗時版型與折疊導覽未保證。頁面載入 Bootstrap 的資源請求與表單提交請求不同，本次「0 請求」指表單操作階段。

未進行第二位代理獨立審查；本紀錄為本次實作及檢查結果。

## 重跑方式

在專案根目錄啟動 `python3 -m http.server 8765 --bind 127.0.0.1`。另啟動 Chrome：

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --remote-debugging-port=9223 \
  --remote-allow-origins=http://localhost:9223 \
  --user-data-dir=/tmp/bmw-chrome-review \
  --no-first-run --no-default-browser-check about:blank
```

在已安裝 `websocket-client` 的 Python 環境執行 `python qa/check_site.py`，會重新產生量測 JSON 與三張截圖。測試輸入僅用虛構資料。

技術依據：[Bootstrap 導覽列](https://getbootstrap.com/docs/5.3/components/navbar/)、[Bootstrap 格線](https://getbootstrap.com/docs/5.3/layout/grid/)。
