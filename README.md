# TradingView Unemployment Data Automation

此專案自動從 Investing.com 抓取美國失業率數據，並格式化為 CSV 以供 TradingView 或其他分析工具使用。

## 最新更新狀態 (2026-02-12)
- **資料格式**：已調整為 `發布日期, 時間, 失業率月份, 實際, 預測, 前值`。
  - 修正了發布時間的時區問題（統一轉為 UTC+8 台北時間）。
  - 自動解析「失業率月份」（例如從 "(Jan)" 轉為 "2026-01"）。
- **腳本優化**：`fetch_unemployment.py` 現在支援**分批抓取 (chunking)**，預設抓取過去 180 天的資料進行增量更新。初次執行或需要歷史資料時，可手動調整腳本中的 `total_days`。

## 專案結構
- `fetch_unemployment.py`：主爬蟲腳本。
  - 會自動建立/更新 `seeds/unemployment_forecast.csv`。
  - 若檔案存在且欄位格式相符，會自動 append 新資料並去重。
- `seeds/unemployment_forecast.csv`：匯出的資料檔。
  - 格式範例：
    ```csv
    發布日期,時間,失業率月份,實際,預測,前值
    2026-01-09,21:30,2025-12,4.4,4.5,4.5
    2026-02-11,21:30,2026-01,4.3,4.4,4.4
    ```
- `requirements.txt`：Python 依賴套件。
- `.github/workflows/update_data.yml`：GitHub Actions 設定檔，用於每日自動執行。

---

## 快速上手

### 1. 安裝環境
確保已安裝 Python 3.9+。

```bash
# 建立虛擬環境 (建議)
python -m venv .venv
# Windows Activate
.\.venv\Scripts\Activate.ps1
# Mac/Linux Activate
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 執行更新
```bash
python fetch_unemployment.py
```
執行後請檢查 `seeds/unemployment_forecast.csv` 是否有最新資料。

### 3. CI/CD 自動化 (GitHub Actions)
本專案已包含 `.github/workflows/update_data.yml`。
- **觸發條件**：每日 00:00 UTC (台北時間 08:00) 或手動觸發 (Workflow Dispatch)。
- **執行內容**：Checkout code -> 安裝 Python -> 執行爬蟲 -> Commit & Push 更新後的 CSV。
- **設定需求**：
  - 將專案 Push 到 GitHub。
  - 確保 Workflow 有權限寫入 Repository (通常在 Settings > Actions > General > Workflow permissions 中勾選 "Read and write permissions")。

## 歷史資料補抓
若需要抓取更長時間的歷史資料（例如 2 年以上），請編輯 `fetch_unemployment.py`：
1. 修改 `total_days` 變數（例如 `365 * 5`）。
2. `fetch_unemployment.py` 內建分批抓取 (Chunking) 機制，會以 90 天為單位分段請求，減少被擋風險。

## 故障排除
- **403 Forbidden**: 可能被 Cloudflare 阻擋。嘗試更新 `cloudscraper` 或稍後再試。
- **欄位錯位**: 若 Investing.com 改版 HTML 結構，可能需要利用 `debug_endpoints_v3.py` (若有保留) 或新增 debug 腳本檢查原始回應。
