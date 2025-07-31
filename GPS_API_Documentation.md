# GPS 路線追蹤 API 文檔

## 概述

GPS 路線追蹤 API 提供完整的 GPS 位置資料管理功能，支援路線上傳、查詢、歷史記錄和刪除操作。本 API 獨立於用戶資料管理系統，專門處理 GPS 路線資料。

## API 端點

### 1. 上傳 GPS 路線資料

**端點**: `POST /gps/upload`

**描述**: 上傳用戶的 GPS 路線資料，支援新增和更新現有路線。

**請求格式**:
```json
{
    "user_id": "1",
    "date": "2025-01-31",
    "route": [
        {
            "lat": 25.047924,
            "lng": 121.517081,
            "ts": "2025-01-31T08:30:00.000Z"
        },
        {
            "lat": 25.046500,
            "lng": 121.516800,
            "ts": "2025-01-31T08:32:00.000Z"
        }
    ]
}
```

**參數說明**:
- `user_id` (string): 用戶 ID
- `date` (string): 日期，格式為 YYYY-MM-DD
- `route` (array): GPS 點陣列
  - `lat` (float): 緯度 (-90 到 90)
  - `lng` (float): 經度 (-180 到 180)
  - `ts` (string): 時間戳記，ISO 8601 格式

**回應範例**:
```json
{
    "message": "GPS 路線上傳成功",
    "user_id": 1,
    "date": "2025-01-31",
    "point_count": 2
}
```

**錯誤回應**:
- `400`: 資料格式錯誤或驗證失敗
- `404`: 用戶不存在
- `500`: 伺服器內部錯誤

---

### 2. 獲取指定日期的 GPS 路線

**端點**: `GET /gps/{user_id}/{date}`

**描述**: 獲取指定用戶在特定日期的 GPS 路線資料。

**路徑參數**:
- `user_id` (integer): 用戶 ID
- `date` (string): 日期，格式為 YYYY-MM-DD

**回應範例**:
```json
{
    "user_id": "1",
    "date": "2025-01-31",
    "route": [
        {
            "lat": 25.047924,
            "lng": 121.517081,
            "ts": "2025-01-31T08:30:00.000Z"
        },
        {
            "lat": 25.046500,
            "lng": 121.516800,
            "ts": "2025-01-31T08:32:00.000Z"
        }
    ]
}
```

**錯誤回應**:
- `400`: 日期格式無效
- `404`: 用戶不存在或找不到指定日期的資料
- `500`: 伺服器內部錯誤

---

### 3. 獲取用戶的 GPS 路線歷史

**端點**: `GET /gps/{user_id}/routes`

**描述**: 獲取用戶的 GPS 路線歷史記錄。

**路徑參數**:
- `user_id` (integer): 用戶 ID

**查詢參數**:
- `limit` (integer, 可選): 限制返回的記錄數量，預設為 30

**回應範例**:
```json
[
    {
        "user_id": "1",
        "date": "2025-01-31",
        "point_count": 5
    },
    {
        "user_id": "1",
        "date": "2025-01-30",
        "point_count": 8
    }
]
```

**錯誤回應**:
- `404`: 用戶不存在
- `500`: 伺服器內部錯誤

---

### 4. 刪除 GPS 路線資料

**端點**: `DELETE /gps/{user_id}/{date}`

**描述**: 刪除指定用戶在特定日期的 GPS 路線資料。

**路徑參數**:
- `user_id` (integer): 用戶 ID
- `date` (string): 日期，格式為 YYYY-MM-DD

**回應範例**:
```json
{
    "message": "GPS 資料刪除成功"
}
```

**錯誤回應**:
- `400`: 日期格式無效
- `404`: 用戶不存在或找不到指定日期的資料
- `500`: 伺服器內部錯誤

---

## 資料驗證規則

### GPS 點資料驗證
- **緯度**: 必須在 -90 到 90 之間
- **經度**: 必須在 -180 到 180 之間
- **時間戳記**: 必須是有效的 ISO 8601 格式

### 路線資料驗證
- **路線點數**: 不能為空，最多允許 10,000 個點
- **日期格式**: 必須是 YYYY-MM-DD 格式
- **用戶 ID**: 必須是有效的數字，且用戶必須存在

---

## 使用範例

### JavaScript/前端整合

```javascript
// 初始化 API 客戶端
const gpsAPI = new GPSRouteAPI('http://localhost:8000');

// 上傳 GPS 路線
const routeData = [
    { lat: 25.047924, lng: 121.517081, ts: "2025-01-31T08:30:00.000Z" },
    { lat: 25.046500, lng: 121.516800, ts: "2025-01-31T08:32:00.000Z" }
];

try {
    const result = await gpsAPI.uploadGPSRoute("1", "2025-01-31", routeData);
    console.log('上傳成功:', result);
} catch (error) {
    console.error('上傳失敗:', error);
}

// 查詢路線資料
try {
    const route = await gpsAPI.getGPSRoute("1", "2025-01-31");
    console.log('路線資料:', route);
} catch (error) {
    console.error('查詢失敗:', error);
}
```

### Python 後端整合

```python
import requests
import json

# 上傳 GPS 路線
def upload_gps_route(user_id, date, route_points):
    url = "http://localhost:8000/gps/upload"
    data = {
        "user_id": user_id,
        "date": date,
        "route": route_points
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"上傳失敗: {response.text}")

# 使用範例
route_data = [
    {"lat": 25.047924, "lng": 121.517081, "ts": "2025-01-31T08:30:00.000Z"},
    {"lat": 25.046500, "lng": 121.516800, "ts": "2025-01-31T08:32:00.000Z"}
]

try:
    result = upload_gps_route("1", "2025-01-31", route_data)
    print("上傳成功:", result)
except Exception as e:
    print("上傳失敗:", e)
```

### cURL 命令範例

```bash
# 上傳 GPS 路線
curl -X POST "http://localhost:8000/gps/upload" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "1",
       "date": "2025-01-31",
       "route": [
         {"lat": 25.047924, "lng": 121.517081, "ts": "2025-01-31T08:30:00.000Z"},
         {"lat": 25.046500, "lng": 121.516800, "ts": "2025-01-31T08:32:00.000Z"}
       ]
     }'

# 查詢指定日期路線
curl -X GET "http://localhost:8000/gps/1/2025-01-31"

# 查詢路線歷史
curl -X GET "http://localhost:8000/gps/1/routes?limit=10"

# 刪除路線資料
curl -X DELETE "http://localhost:8000/gps/1/2025-01-31"
```

---

## 資料庫結構

### GPS 路線表 (gps_routes)
- `id`: 主鍵
- `user_id`: 用戶 ID（外鍵）
- `date`: 日期
- `route_data`: JSON 格式的路線資料
- `created_at`: 建立時間
- `updated_at`: 更新時間

### GPS 點表 (gps_points)
- `id`: 主鍵
- `route_id`: 路線 ID（外鍵）
- `latitude`: 緯度
- `longitude`: 經度
- `timestamp`: 時間戳記
- `created_at`: 建立時間

---

## 效能考量

- **路線點數限制**: 單次上傳最多 10,000 個 GPS 點
- **查詢歷史限制**: 預設返回最近 30 條記錄，可調整
- **資料索引**: 在 user_id 和 date 欄位上建立索引以提升查詢效能
- **JSON 儲存**: 路線資料以 JSON 格式儲存，適合複雜的路線結構

---

## 安全性

- **用戶驗證**: 所有操作都會驗證用戶是否存在
- **資料驗證**: 嚴格的 GPS 座標和日期格式驗證
- **錯誤處理**: 完整的錯誤訊息和狀態碼回應
- **交易保護**: 資料庫操作使用交易確保資料一致性

---

## 未來擴展

可能的功能擴展：
1. **路線分析**: 計算距離、速度、停留時間等統計資料
2. **路線共享**: 允許用戶分享路線給其他用戶
3. **路線搜尋**: 按地理區域或路線特徵搜尋
4. **批次操作**: 支援批次上傳和刪除操作
5. **即時追蹤**: WebSocket 支援即時位置更新
