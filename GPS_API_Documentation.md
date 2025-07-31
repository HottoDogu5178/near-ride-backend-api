# GPS 路線追蹤 API 文檔

## 概述

GPS 路線追蹤 API 提供完整的 GPS 位置資料管理功能，支援詳細軌跡記錄、路線統計分析、歷史記錄查詢和資料管理。本 API 獨立於用戶資料管理系統，專門處理用戶移動軌跡的完整記錄。

## 🆕 增強功能

- **完整軌跡記錄**: 記錄所有 GPS 資料點，包含位置、時間、海拔、精度、速度、方向
- **自動距離計算**: 使用 Haversine 公式計算軌跡總距離
- **時間統計**: 自動計算開始/結束時間和持續時間
- **詳細分析**: 提供軌跡統計和分析資料
- **大容量支援**: 支援最多 50,000 個 GPS 點記錄

## API 端點

### 1. 上傳 GPS 路線資料（增強版）

**端點**: `POST /gps/upload`

**描述**: 上傳用戶的 GPS 路線資料，支援完整軌跡記錄和自動統計計算。

**請求格式**:
```json
{
    "user_id": "1",
    "date": "2025-07-31",
    "route": [
        {
            "lat": 25.047924,
            "lng": 121.517081,
            "ts": "2025-07-31T08:30:00.000Z",
            "altitude": 10.5,
            "accuracy": 5.0,
            "speed": 0.0,
            "heading": 0.0
        },
        {
            "lat": 25.047800,
            "lng": 121.517200,
            "ts": "2025-07-31T08:30:30.000Z",
            "altitude": 10.8,
            "accuracy": 4.5,
            "speed": 1.2,
            "heading": 45.0
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
  - `altitude` (float, 可選): 海拔高度（公尺）
  - `accuracy` (float, 可選): GPS 精度（公尺）
  - `speed` (float, 可選): 速度（公尺/秒）
  - `heading` (float, 可選): 方向角（0-360 度）

**回應範例**:
```json
{
    "message": "GPS 路線上傳成功",
    "user_id": 1,
    "date": "2025-07-31",
    "point_count": 15,
    "total_distance": 5238.67,
    "start_time": "2025-07-31T08:30:00+00:00",
    "end_time": "2025-07-31T08:43:30+00:00"
}
```

**錯誤回應**:
- `400`: 資料格式錯誤或驗證失敗
- `404`: 用戶不存在
- `500`: 伺服器內部錯誤

---

### 2. 獲取指定日期的 GPS 路線（含統計）

**端點**: `GET /gps/{user_id}/{date}`

**描述**: 獲取指定用戶在特定日期的 GPS 路線資料和完整統計資訊。

**路徑參數**:
- `user_id` (integer): 用戶 ID
- `date` (string): 日期，格式為 YYYY-MM-DD

**回應範例**:
```json
{
    "user_id": "1",
    "date": "2025-07-31",
    "route": [
        {
            "lat": 25.047924,
            "lng": 121.517081,
            "ts": "2025-07-31T08:30:00.000Z",
            "altitude": 10.5,
            "accuracy": 5.0,
            "speed": 0.0,
            "heading": 0.0
        }
    ],
    "statistics": {
        "total_points": 15,
        "total_distance": 5238.67,
        "start_time": "2025-07-31T08:30:00+00:00",
        "end_time": "2025-07-31T08:43:30+00:00",
        "duration_minutes": 13.5
    }
}
```

### 3. 獲取詳細 GPS 點資料

**端點**: `GET /gps/{user_id}/{date}/points`

**描述**: 獲取指定日期路線的所有詳細 GPS 點資料。

**路徑參數**:
- `user_id` (integer): 用戶 ID
- `date` (string): 日期，格式為 YYYY-MM-DD

**回應範例**:
```json
{
    "user_id": "1",
    "date": "2025-07-31",
    "points": [
        {
            "latitude": 25.047924,
            "longitude": 121.517081,
            "timestamp": "2025-07-31T08:30:00",
            "altitude": 10.5,
            "accuracy": 5.0,
            "speed": 0.0,
            "heading": 0.0
        }
    ],
    "total_points": 15
}
```

### 4. 獲取用戶的 GPS 路線歷史（增強版）

**端點**: `GET /gps/{user_id}/routes`

**描述**: 獲取用戶的 GPS 路線歷史記錄，包含完整統計資訊。

**路徑參數**:
- `user_id` (integer): 用戶 ID

**查詢參數**:
- `limit` (integer, 可選): 限制返回的記錄數量，預設為 30

**回應範例**:
```json
[
    {
        "user_id": "1",
        "date": "2025-07-31",
        "point_count": 15,
        "total_distance": 5238.67,
        "start_time": "2025-07-31T08:30:00+00:00",
        "end_time": "2025-07-31T08:43:30+00:00",
        "duration_minutes": 13.5
    },
    {
        "user_id": "1",
        "date": "2025-07-30",
        "point_count": 22,
        "total_distance": 8756.23,
        "start_time": "2025-07-30T07:45:00+00:00",
        "end_time": "2025-07-30T08:15:00+00:00",
        "duration_minutes": 30.0
    }
]
```

**錯誤回應**:
- `404`: 用戶不存在
- `500`: 伺服器內部錯誤

### 5. 刪除 GPS 路線資料

**端點**: `DELETE /gps/{user_id}/{date}`

**描述**: 刪除指定用戶在特定日期的 GPS 路線資料和所有相關點資料。

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
- **海拔高度**: 可選，數值型態（公尺）
- **GPS 精度**: 可選，正數（公尺）
- **速度**: 可選，非負數（公尺/秒）
- **方向角**: 可選，0-360 度之間

### 路線資料驗證
- **路線點數**: 不能為空，最多允許 50,000 個點
- **日期格式**: 必須是 YYYY-MM-DD 格式
- **用戶 ID**: 必須是有效的數字，且用戶必須存在

---

## 軌跡統計功能

### 自動計算統計資料
- **總距離**: 使用 Haversine 公式計算各點間距離總和
- **開始/結束時間**: 自動從 GPS 點時間戳記中提取
- **持續時間**: 自動計算軌跡總時長（分鐘）
- **點數統計**: 記錄軌跡中的總 GPS 點數

### 距離計算公式
使用 Haversine 公式計算地球表面兩點間的大圓距離：

```
a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
c = 2 ⋅ atan2( √a, √(1−a) )
d = R ⋅ c
```

其中：
- φ 是緯度
- λ 是經度
- R 是地球半徑（6,371,000 公尺）
- d 是兩點間距離

---

## 使用範例

### JavaScript/前端整合

```javascript
// 上傳增強版 GPS 軌跡
const routeData = [
    { 
        lat: 25.047924, 
        lng: 121.517081, 
        ts: "2025-07-31T08:30:00.000Z",
        altitude: 10.5,
        accuracy: 5.0,
        speed: 0.0,
        heading: 0.0
    },
    { 
        lat: 25.047800, 
        lng: 121.517200, 
        ts: "2025-07-31T08:30:30.000Z",
        altitude: 10.8,
        accuracy: 4.5,
        speed: 1.2,
        heading: 45.0
    }
];

try {
    const result = await fetch('/gps/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: "1",
            date: "2025-07-31",
            route: routeData
        })
    }).then(r => r.json());
    
    console.log('軌跡上傳成功:', result);
    console.log(`總距離: ${result.total_distance.toFixed(2)} 公尺`);
    console.log(`持續時間: ${result.end_time - result.start_time} 分鐘`);
} catch (error) {
    console.error('上傳失敗:', error);
}

// 查詢詳細 GPS 點資料
try {
    const points = await fetch('/gps/1/2025-07-31/points').then(r => r.json());
    console.log('GPS 點資料:', points.points);
    
    points.points.forEach((point, index) => {
        console.log(`點 ${index + 1}:`);
        console.log(`  位置: ${point.latitude}, ${point.longitude}`);
        console.log(`  海拔: ${point.altitude}m, 精度: ${point.accuracy}m`);
        console.log(`  速度: ${point.speed}m/s, 方向: ${point.heading}°`);
    });
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
