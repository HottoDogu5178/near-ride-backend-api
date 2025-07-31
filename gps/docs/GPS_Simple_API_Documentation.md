# 簡化 GPS 系統 API 文檔

## 概述
本系統提供簡化的 GPS 定位記錄功能，僅記錄用戶、經緯度和時間。路徑計算和軌跡分析將在後續版本中實現。

## API 端點

### 1. 記錄 GPS 定位
**端點**: `POST /gps/location`
**參數**: `user_id` (查詢參數)
**請求體**:
```json
{
  "lat": 25.0330,
  "lng": 121.5654, 
  "ts": "2025-07-31T16:16:37.066177"
}
```

**回應**:
```json
{
  "message": "GPS 定位記錄成功",
  "id": 1,
  "user_id": 1,
  "latitude": 25.033,
  "longitude": 121.5654,
  "timestamp": "2025-07-31T16:16:37.066177"
}
```

### 2. 獲取用戶定位歷史
**端點**: `GET /gps/locations/{user_id}`
**可選參數**:
- `start_date`: YYYY-MM-DD 格式
- `end_date`: YYYY-MM-DD 格式  
- `limit`: 限制返回數量（默認 1000）

**回應**:
```json
{
  "user_id": 1,
  "total_locations": 4,
  "locations": [
    {
      "id": 4,
      "latitude": 25.036,
      "longitude": 121.568,
      "timestamp": "2025-07-31T16:16:37.066177"
    }
  ]
}
```

### 3. 按日期獲取定位記錄
**端點**: `GET /gps/locations/{user_id}/date/{date}`
**日期格式**: YYYY-MM-DD

**回應**:
```json
{
  "user_id": 1,
  "date": "2025-07-31",
  "total_locations": 4,
  "locations": [...同上...]
}
```

### 4. 刪除定位記錄
**端點**: `DELETE /gps/locations/{user_id}`
**可選參數**:
- `start_date`: YYYY-MM-DD 格式
- `end_date`: YYYY-MM-DD 格式

**回應**:
```json
{
  "message": "GPS 定位記錄刪除成功",
  "deleted_count": 2
}
```

## 資料庫架構

### GPS_locations 表
```sql
CREATE TABLE gps_locations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 索引
```sql
CREATE INDEX idx_gps_locations_user_id ON gps_locations(user_id);
CREATE INDEX idx_gps_locations_timestamp ON gps_locations(timestamp);
CREATE INDEX idx_gps_locations_user_timestamp ON gps_locations(user_id, timestamp);
```

## 前端整合

### JavaScript 範例
```javascript
// 記錄當前位置
async function recordCurrentLocation(userId) {
  if (!navigator.geolocation) {
    console.error('瀏覽器不支援地理定位');
    return;
  }

  navigator.geolocation.getCurrentPosition(async (position) => {
    const locationData = {
      lat: position.coords.latitude,
      lng: position.coords.longitude,
      ts: new Date().toISOString()
    };

    try {
      const response = await fetch(`/gps/location?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(locationData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('GPS 定位記錄成功:', result);
      } else {
        console.error('GPS 定位記錄失敗:', await response.text());
      }
    } catch (error) {
      console.error('網路錯誤:', error);
    }
  }, (error) => {
    console.error('獲取位置失敗:', error);
  });
}

// 獲取用戶今日的定位歷史
async function getTodayLocations(userId) {
  const today = new Date().toISOString().split('T')[0];
  
  try {
    const response = await fetch(`/gps/locations/${userId}/date/${today}`);
    
    if (response.ok) {
      const result = await response.json();
      console.log(`今日共有 ${result.total_locations} 個定位記錄`);
      return result.locations;
    } else {
      console.error('查詢失敗:', await response.text());
    }
  } catch (error) {
    console.error('網路錯誤:', error);
  }
}

// 定期記錄位置（每5分鐘）
function startLocationTracking(userId) {
  recordCurrentLocation(userId); // 立即記錄一次
  
  setInterval(() => {
    recordCurrentLocation(userId);
  }, 5 * 60 * 1000); // 5分鐘
}
```

## 驗證規則
- 緯度：-90 到 90 度
- 經度：-180 到 180 度  
- 時間戳：ISO 8601 格式
- 用戶 ID：必須存在於用戶表中

## 錯誤處理
- 400：資料驗證失敗
- 404：用戶不存在或找不到記錄
- 422：請求格式錯誤
- 500：服務器內部錯誤

## 使用注意事項
1. 此版本僅記錄基本的 GPS 定位資料
2. 路徑計算、距離統計等功能將在後續版本實現
3. 建議前端實現合理的記錄頻率，避免過度請求
4. 定位資料按時間倒序排列，最新記錄在前
