# GPS 系統架構總覽

## 📁 檔案結構
```
gps/
├── README.md                              # GPS 系統總覽
├── docs/                                  # 📚 文檔資料夾
│   ├── GPS_Simple_API_Documentation.md   # API 文檔
│   └── Frontend_Integration_Guide.md     # 前端整合指南
├── tests/                                 # 🧪 測試檔案
│   └── test_simple_gps.py               # 主要測試檔
├── frontend/                              # 🌐 前端整合檔案
│   ├── frontend_gps_examples.js         # 前端範例
│   └── gps_frontend_integration.js      # 整合腳本
└── legacy/                               # 📦 舊版本檔案（已棄用）
    ├── GPS_API_Documentation.md         # 舊版 API 文檔
    ├── test_gps_api.py                  # 舊版測試檔
    ├── test_gps_routes.py               # 路線測試檔
    ├── test_enhanced_gps.py             # 增強版測試檔
    ├── test_comprehensive.py            # 綜合測試檔
    ├── gps_routes_clean.py              # 清理版路由
    └── gps_routes_new.py                # 新版路由

app/
├── models/
│   └── gps_route.py                      # 🗂️ GPS 資料模型
└── routes/
    └── gps_routes.py                     # 🛣️ GPS API 路由
```

## 🎯 系統特點

### ✅ 當前版本（簡化版）
- **簡單直接**: 每次只記錄一個 GPS 點
- **基本資料**: 用戶 ID、經緯度、時間戳
- **高效能**: 無複雜計算，響應速度快
- **易擴展**: 為未來功能提供基礎資料

### 📋 核心功能
1. **GPS 定位記錄** - 記錄單個定位點
2. **歷史查詢** - 獲取用戶定位歷史
3. **日期篩選** - 按日期查詢定位記錄
4. **資料管理** - 刪除定位記錄
5. **資料驗證** - 經緯度範圍檢查

## 🔧 技術架構

### 後端 (FastAPI)
- **框架**: FastAPI + SQLAlchemy
- **資料庫**: PostgreSQL
- **驗證**: Pydantic 資料驗證
- **日誌**: Python logging

### 前端整合
- **原生 JavaScript**: 完整的 GPSTracker 類別
- **HTML 範例**: 即用的測試頁面
- **React Hook**: useGPSTracker 自定義 Hook

### 資料模型
```python
class GPSLocation(Base):
    id = Integer (Primary Key)
    user_id = Integer (Foreign Key)
    latitude = Float
    longitude = Float
    timestamp = DateTime
    created_at = DateTime (Auto)
```

## 📊 API 端點總覽

| 方法 | 端點 | 功能 | 參數 |
|------|------|------|------|
| POST | `/gps/location` | 記錄 GPS 定位 | user_id, lat, lng, ts |
| GET | `/gps/locations/{user_id}` | 獲取定位歷史 | start_date, end_date, limit |
| GET | `/gps/locations/{user_id}/date/{date}` | 按日期查詢 | date (YYYY-MM-DD) |
| DELETE | `/gps/locations/{user_id}` | 刪除定位記錄 | start_date, end_date |

## 🧪 測試涵蓋範圍

### 自動化測試
- ✅ GPS 定位記錄功能
- ✅ 定位歷史查詢
- ✅ 資料驗證（經緯度範圍）
- ✅ 按日期篩選查詢
- ✅ 批量記錄測試
- ✅ 刪除操作測試

### 測試執行
```bash
cd gps/tests
python test_simple_gps.py
```

## 🚀 使用方式

### 快速開始
1. **啟動服務器**
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

2. **記錄定位**
   ```bash
   curl -X POST "http://localhost:8001/gps/location?user_id=1" \
     -H "Content-Type: application/json" \
     -d '{"lat": 25.0330, "lng": 121.5654, "ts": "2025-07-31T16:16:37"}'
   ```

3. **查詢歷史**
   ```bash
   curl "http://localhost:8001/gps/locations/1"
   ```

### 前端整合
參考 `docs/Frontend_Integration_Guide.md` 獲取完整的前端整合範例。

## 📈 開發歷程

### 版本歷史
- **v1.0** (當前版本) - 簡化 GPS 系統
  - 基本定位記錄功能
  - 簡潔的 API 設計
  - 完整的測試覆蓋

- **v0.x** (已棄用) - 複雜軌跡系統
  - 軌跡計算和統計
  - 路線分析功能
  - 複雜的資料結構

### 設計原則
1. **簡單優先** - 先實現基本功能
2. **資料導向** - 專注於資料收集
3. **易於維護** - 清晰的程式碼結構
4. **測試驅動** - 完整的測試覆蓋

## 🔮 未來規劃

### 短期目標
- [ ] 資料分頁功能
- [ ] GPS 精度記錄
- [ ] 批量上傳 API
- [ ] 即時定位推送

### 長期目標
- [ ] 路徑計算模組
- [ ] 軌跡可視化
- [ ] 位置分析工具
- [ ] 隱私保護機制

## 🛠️ 維護指南

### 主要檔案
- **API 邏輯**: `app/routes/gps_routes.py`
- **資料模型**: `app/models/gps_route.py`
- **測試檔案**: `gps/tests/test_simple_gps.py`
- **文檔**: `gps/docs/`

### 開發流程
1. 修改 API 邏輯
2. 更新資料模型（如需要）
3. 執行測試驗證
4. 更新相關文檔

### 問題排查
- **API 錯誤**: 檢查 FastAPI 日誌
- **資料庫問題**: 檢查 PostgreSQL 連接
- **測試失敗**: 確認服務器運行狀態

## 📞 支援資源

- **API 文檔**: `/docs` (Swagger UI)
- **測試頁面**: `gps/frontend/` 中的範例
- **GitHub**: 專案儲存庫
- **問題回報**: GitHub Issues

---

**維護者**: 開發團隊  
**最後更新**: 2025-07-31  
**版本**: 1.0.0
