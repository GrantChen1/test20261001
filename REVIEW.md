# 汽車展示教學網站修訂與實測紀錄

檢查日期：2026-10-01（Asia/Taipei）  
依據：`bmw_teaching_plan.md` 與統籌者轉述的 Claude Code 第 1 輪意見。

目前狀態：**WAITING_FOR_CLAUDE_RECHECK**。本輪修訂及必要重測完成，等候 Claude 唯讀複查；未宣稱複查通過。

## 本輪必要修訂（Claude 第 1 輪回應）

五項均採用，選擇較精簡的實作：

1. 三張車卡以語意化 dl/dt/dd 加入同名的「動力、座位、情境」三項屬性，每卡明標虛構示意、非真車規格。未另外增加重複比較表。
2. 移除三卡舊 aria-label；以可見「了解示範流程」接 visually-hidden 車名，保留連續的可見文字與個別名稱。
3. 移除膠囊及其樣式，改成一般段落「分類索引（靜態文字）」，未加入篩選功能。
4. 主標題從 12ch 改為 11em 及 text-wrap:balance，沒有硬插換行。
5. 教學計畫標明教師示範完成版與教師提供的進階焦點程式；補六節各 50 分鐘的可調整草案、每節可量測產出、五面向三級評分描述與計分方式。

逐項採用／不採用理由及審查時間差：[COORDINATION.md](COORDINATION.md)。不增加輪播、篩選或比較互動；未收到的其他具體意見不臆測。

## 本輪受影響項目的實測

沿用前輪 Chrome/CDP 方法；使用獨立本機 HTTP port 8766。只重跑新增屬性後的排版、連結名稱／目標、靜態分類、主標題及手機選單至車款區的焦點路徑。未重跑整套表單／儲存測試：程式實際比對確認 form HTML 完全一致，忽略註解後的 inline JavaScript 也完全一致。表單仍只作前端示範；前輪的 0 傳送／0 儲存結果按其原本測試範圍保留。

| viewport | scrollWidth | 卡片欄數／寬度／高度 | 主標題 | 結果 |
|---|---:|---|---|---|
| 375px | 360px | 1 欄／336px／489.61px | 完整單行 | 無橫向溢出；屬性可讀 |
| 768px | 753px | 2 欄／336px／491.02px | 完整單行 | 第三卡下一列；無橫向溢出 |
| 1440px | 1425px | 3 欄／416px／492.58px | 完整單行 | 三卡等高；無橫向溢出 |

- 三張新截圖均已視覺檢視，新增屬性、分類文字及標題沒有裁切／重疊，表單仍可見。這些截圖未進行有效提交，沒有成功提示。
- 三卡皆為相同三項屬性，每卡皆有虛構標示；卡內文字、屬性及連結的 scrollWidth 未大於 clientWidth。
- Chrome Accessibility tree 的實際連結名稱為「了解示範流程 ：Aero One／Vista Two／Motion Three」（空白由瀏覽器正規化）。三者都連續包含可見文字及車名；各連結仍到達 #contact。
- 分類膠囊 DOM 及 CSS 已移除；一般段落明寫「靜態文字」，沒有新互動控制項。
- 375px 鍵盤：Enter 展開選單，Tab 至車款連結，Enter 導覽到 #models；選單收合、焦點落在 models。既有進階焦點程式只修改教學註解。
- HTML 巢狀配對、ID 唯一性及錨點有效性通過；本輪 Chrome JavaScript 執行錯誤 0。
- 教學文件人工核對：6 列課程、每列時間合計 50 分鐘、每節可量測交付；五面向權重 20/25/20/20/15 合計 100%，每面向三級描述與計分方法俱全。

證據：[本輪量測 JSON](qa/round2/results.json)、[375px](qa/round2/375.png)、[768px](qa/round2/768.png)、[1440px](qa/round2/1440.png)、[必要重測程式](qa/check_round2.py)。JSON 含本輪 index.html 的 SHA-256，方便複查時辨識版本。

重跑本輪：啟動 `python3 -m http.server 8766 --bind 127.0.0.1`，使用下方相同的 Chrome port 9223 啟動方式，在已安裝 websocket-client 的 Python 環境執行 `python qa/check_round2.py`。它只取用 check_site.py 的 CDP 輔助函式，不執行前輪完整測試。

本輪仍限於 Chrome 模擬寬度；前輪列出的原生 select、實體裝置、其他瀏覽器、完整無障礙及 CDN 限制均保留。下一步是 Claude 唯讀複查。

## 前輪修訂與實測（歷史紀錄）

以下為前輪記錄；當時教學計畫未改。前輪網站、計畫、REVIEW、JSON 與截圖已備份於 `qa/round1/`，其中排版數據不代表本輪新增屬性後的卡片高度。

### 前輪修訂內容與原因

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

前輪 Codex 實測完成時尚未納入第二位代理的審查結論。本輪已依統籌者提供的 Claude 第 1 輪五項意見修訂；Claude 複查仍待進行。審查時間差見 COORDINATION.md。

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
