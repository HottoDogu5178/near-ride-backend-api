# GPS 定位系統

## 概述
這是一個簡化的 GPS 定位記錄系統，專注於基本的定位資料存儲。系統只記錄用戶、經緯度和時間戳，路徑計算和軌跡分析功能將在未來版本中實現。

## 檔案結構
```
gps/
├── docs/                          # 文檔資料夾
│   └── GPS_Simple_API_Documentation.md
├── tests/                         # 測試檔案
│   └── test_simple_gps.py
├── frontend/                      # 前端整合檔案
│   ├── frontend_gps_examples.js
│   └── gps_frontend_integration.js
├── legacy/                        # 舊版本檔案（已棄用）
│   ├── GPS_API_Documentation.md
│   ├── test_gps_api.py
│   ├── test_gps_routes.py
│   ├── test_enhanced_gps.py
│   ├── test_comprehensive.py
│   ├── gps_routes_clean.py
│   └── gps_routes_new.py
└── README.md                      # 本檔案
```

## 當前版本功能

### 核心模型
- **GPSLocation**: 簡化的 GPS 定位模型
  - `user_id`: 用戶 ID
  - `latitude`: 緯度
  - `longitude`: 經度  
  - `timestamp`: 時間戳
  - `created_at`: 記錄創建時間

### API 端點
- `POST /gps/location` - 記錄單個 GPS 定位點
- `GET /gps/locations/{user_id}` - 獲取用戶定位歷史
- `GET /gps/locations/{user_id}/date/{date}` - 按日期查詢定位記錄
- `DELETE /gps/locations/{user_id}` - 刪除用戶定位記錄

### 資料驗證
- 緯度範圍：-90 到 90 度
- 經度範圍：-180 到 180 度
- 時間戳格式：ISO 8601

## 使用方式

### 記錄 GPS 定位
```bash
curl -X POST "http://localhost:8001/gps/location?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 25.0330,
    "lng": 121.5654,
    "ts": "2025-07-31T16:16:37.066177"
  }'
```

### 查詢定位歷史
```bash
curl "http://localhost:8001/gps/locations/1"
```

### 按日期查詢
```bash
curl "http://localhost:8001/gps/locations/1/date/2025-07-31"
```

## 測試

### 執行測試
```bash
cd gps/tests
python test_simple_gps.py
```

### 測試涵蓋範圍
- GPS 定位記錄功能
- 資料驗證
- 定位歷史查詢
- 按日期篩選
- 刪除操作

## 前端整合

參考 `frontend/` 資料夾中的範例檔案：
- `frontend_gps_examples.js` - 基本 JavaScript 整合範例
- `gps_frontend_integration.js` - 完整的前端整合方案

## 資料庫架構

### GPS Locations 表
```sql
CREATE TABLE gps_locations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_gps_locations_user_id ON gps_locations(user_id);
CREATE INDEX idx_gps_locations_timestamp ON gps_locations(timestamp);
CREATE INDEX idx_gps_locations_user_timestamp ON gps_locations(user_id, timestamp);
```

## 開發歷程

### 版本 1.0（當前版本）- 簡化 GPS 系統
- 基本的 GPS 定位記錄
- 簡單的 CRUD 操作
- 資料驗證和錯誤處理
- 按日期篩選功能

### 歷史版本（已棄用）
舊版本的檔案已移至 `legacy/` 資料夾，包含：
- 複雜的軌跡計算系統
- 增強的統計功能
- 路線分析工具

這些功能因為複雜性和實際需求不符而被簡化。

## 未來規劃

1. **路徑計算模組**
   - 基於存儲的 GPS 點計算距離
   - 軌跡重建和可視化
   
2. **位置分析**
   - 停留點檢測
   - 活動模式分析
   
3. **效能優化**
   - 資料分頁
   - 快取機制
   
4. **隱私保護**
   - 資料加密
   - 權限控制

## 維護說明

- 主要邏輯位於 `app/routes/gps_routes.py`
- 資料模型位於 `app/models/gps_route.py`
- 測試使用 `gps/tests/test_simple_gps.py`
- API 文檔位於 `gps/docs/GPS_Simple_API_Documentation.md`

如需協助或有問題，請參考相關文檔或聯繫開發團隊。
