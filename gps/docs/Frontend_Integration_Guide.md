# GPS 前端整合指南

## 概述
本指南說明如何在前端應用中整合 GPS 定位系統，包括基本的定位記錄、查詢和顯示功能。

## 快速開始

### 1. 基本 GPS 定位記錄

```javascript
// GPS 定位記錄類
class GPSTracker {
    constructor(baseUrl = 'http://localhost:8001', userId) {
        this.baseUrl = baseUrl;
        this.userId = userId;
        this.watchId = null;
        this.isTracking = false;
    }

    // 檢查瀏覽器是否支援地理定位
    isGeolocationSupported() {
        return 'geolocation' in navigator;
    }

    // 記錄當前位置
    async recordCurrentLocation() {
        if (!this.isGeolocationSupported()) {
            throw new Error('瀏覽器不支援地理定位');
        }

        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    try {
                        const result = await this.saveLocation(
                            position.coords.latitude,
                            position.coords.longitude
                        );
                        resolve(result);
                    } catch (error) {
                        reject(error);
                    }
                },
                (error) => {
                    reject(this.handleGeolocationError(error));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            );
        });
    }

    // 保存位置到服務器
    async saveLocation(latitude, longitude, timestamp = null) {
        const locationData = {
            lat: latitude,
            lng: longitude,
            ts: timestamp || new Date().toISOString()
        };

        const response = await fetch(
            `${this.baseUrl}/gps/location?user_id=${this.userId}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(locationData)
            }
        );

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`GPS 定位記錄失敗: ${error}`);
        }

        return await response.json();
    }

    // 開始持續追蹤
    startTracking(intervalMinutes = 5) {
        if (this.isTracking) {
            console.warn('GPS 追蹤已在執行中');
            return;
        }

        this.isTracking = true;
        
        // 立即記錄一次
        this.recordCurrentLocation().catch(console.error);

        // 設定定期記錄
        this.trackingInterval = setInterval(() => {
            if (this.isTracking) {
                this.recordCurrentLocation().catch(console.error);
            }
        }, intervalMinutes * 60 * 1000);

        console.log(`GPS 追蹤已開始，每 ${intervalMinutes} 分鐘記錄一次`);
    }

    // 停止追蹤
    stopTracking() {
        if (!this.isTracking) {
            return;
        }

        this.isTracking = false;
        
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }

        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }

        console.log('GPS 追蹤已停止');
    }

    // 獲取用戶定位歷史
    async getLocationHistory(startDate = null, endDate = null, limit = 1000) {
        let url = `${this.baseUrl}/gps/locations/${this.userId}?limit=${limit}`;
        
        if (startDate) {
            url += `&start_date=${startDate}`;
        }
        if (endDate) {
            url += `&end_date=${endDate}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`獲取定位歷史失敗: ${error}`);
        }

        return await response.json();
    }

    // 獲取指定日期的定位記錄
    async getLocationsByDate(date) {
        const response = await fetch(
            `${this.baseUrl}/gps/locations/${this.userId}/date/${date}`
        );

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`獲取 ${date} 定位記錄失敗: ${error}`);
        }

        return await response.json();
    }

    // 刪除定位記錄
    async deleteLocations(startDate = null, endDate = null) {
        let url = `${this.baseUrl}/gps/locations/${this.userId}`;
        const params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url, { method: 'DELETE' });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`刪除定位記錄失敗: ${error}`);
        }

        return await response.json();
    }

    // 處理地理定位錯誤
    handleGeolocationError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                return new Error('用戶拒絕地理定位請求');
            case error.POSITION_UNAVAILABLE:
                return new Error('無法獲取位置資訊');
            case error.TIMEOUT:
                return new Error('獲取位置請求超時');
            default:
                return new Error('獲取位置時發生未知錯誤');
        }
    }
}

// 使用範例
const gpsTracker = new GPSTracker('http://localhost:8001', 1);

// 檢查支援性
if (gpsTracker.isGeolocationSupported()) {
    console.log('瀏覽器支援地理定位');
} else {
    console.error('瀏覽器不支援地理定位');
}
```

### 2. HTML 整合範例

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPS 定位系統測試</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        button { margin: 5px; padding: 10px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .info { background-color: #d1ecf1; color: #0c5460; }
        #locationHistory { max-height: 400px; overflow-y: auto; }
        .location-item { 
            border: 1px solid #ddd; 
            margin: 5px 0; 
            padding: 10px; 
            border-radius: 5px; 
        }
    </style>
</head>
<body>
    <h1>GPS 定位系統測試</h1>
    
    <div class="controls">
        <button onclick="recordLocation()">記錄當前位置</button>
        <button onclick="startTracking()">開始追蹤</button>
        <button onclick="stopTracking()">停止追蹤</button>
        <button onclick="loadHistory()">載入歷史記錄</button>
        <button onclick="loadTodayLocations()">載入今日記錄</button>
        <button onclick="clearAllLocations()">清空所有記錄</button>
    </div>

    <div id="status" class="status info">準備就緒</div>

    <h2>定位歷史</h2>
    <div id="locationHistory"></div>

    <script>
        // 全域變數
        let gpsTracker;
        const userId = 1; // 替換為實際用戶 ID

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            gpsTracker = new GPSTracker('http://localhost:8001', userId);
            updateStatus('GPS 追蹤器已初始化', 'info');
        });

        // 更新狀態顯示
        function updateStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
        }

        // 記錄當前位置
        async function recordLocation() {
            try {
                updateStatus('正在獲取位置...', 'info');
                const result = await gpsTracker.recordCurrentLocation();
                updateStatus(`位置記錄成功 (ID: ${result.id})`, 'success');
                console.log('位置記錄:', result);
            } catch (error) {
                updateStatus(`記錄位置失敗: ${error.message}`, 'error');
                console.error('記錄位置錯誤:', error);
            }
        }

        // 開始追蹤
        function startTracking() {
            try {
                gpsTracker.startTracking(1); // 每分鐘記錄一次（測試用）
                updateStatus('GPS 追蹤已開始', 'success');
            } catch (error) {
                updateStatus(`開始追蹤失敗: ${error.message}`, 'error');
            }
        }

        // 停止追蹤
        function stopTracking() {
            gpsTracker.stopTracking();
            updateStatus('GPS 追蹤已停止', 'info');
        }

        // 載入歷史記錄
        async function loadHistory() {
            try {
                updateStatus('正在載入歷史記錄...', 'info');
                const history = await gpsTracker.getLocationHistory();
                displayLocations(history.locations);
                updateStatus(`載入了 ${history.total_locations} 個位置記錄`, 'success');
            } catch (error) {
                updateStatus(`載入歷史記錄失敗: ${error.message}`, 'error');
            }
        }

        // 載入今日記錄
        async function loadTodayLocations() {
            try {
                const today = new Date().toISOString().split('T')[0];
                updateStatus('正在載入今日記錄...', 'info');
                const todayData = await gpsTracker.getLocationsByDate(today);
                displayLocations(todayData.locations);
                updateStatus(`載入了今日 ${todayData.total_locations} 個位置記錄`, 'success');
            } catch (error) {
                updateStatus(`載入今日記錄失敗: ${error.message}`, 'error');
            }
        }

        // 清空所有記錄
        async function clearAllLocations() {
            if (!confirm('確定要刪除所有定位記錄嗎？')) {
                return;
            }

            try {
                updateStatus('正在刪除記錄...', 'info');
                const result = await gpsTracker.deleteLocations();
                updateStatus(`成功刪除 ${result.deleted_count} 個記錄`, 'success');
                document.getElementById('locationHistory').innerHTML = '';
            } catch (error) {
                updateStatus(`刪除記錄失敗: ${error.message}`, 'error');
            }
        }

        // 顯示位置記錄
        function displayLocations(locations) {
            const container = document.getElementById('locationHistory');
            
            if (!locations || locations.length === 0) {
                container.innerHTML = '<p>沒有位置記錄</p>';
                return;
            }

            const html = locations.map(location => {
                const date = new Date(location.timestamp);
                return `
                    <div class="location-item">
                        <strong>ID:</strong> ${location.id}<br>
                        <strong>座標:</strong> ${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}<br>
                        <strong>時間:</strong> ${date.toLocaleString('zh-TW')}<br>
                        <a href="https://www.google.com/maps?q=${location.latitude},${location.longitude}" target="_blank">在 Google Maps 中查看</a>
                    </div>
                `;
            }).join('');

            container.innerHTML = html;
        }

        // 在此處插入 GPSTracker 類別定義...
        ${上面的 GPSTracker 類別程式碼}
    </script>
</body>
</html>
```

### 3. React 整合範例

```jsx
import React, { useState, useEffect, useCallback } from 'react';

// GPS Hook
const useGPSTracker = (baseUrl, userId) => {
    const [tracker, setTracker] = useState(null);
    const [isTracking, setIsTracking] = useState(false);
    const [locations, setLocations] = useState([]);
    const [status, setStatus] = useState('準備就緒');

    useEffect(() => {
        const gpsTracker = new GPSTracker(baseUrl, userId);
        setTracker(gpsTracker);
    }, [baseUrl, userId]);

    const recordLocation = useCallback(async () => {
        if (!tracker) return;

        try {
            setStatus('正在記錄位置...');
            const result = await tracker.recordCurrentLocation();
            setStatus(`位置記錄成功 (ID: ${result.id})`);
            return result;
        } catch (error) {
            setStatus(`記錄失敗: ${error.message}`);
            throw error;
        }
    }, [tracker]);

    const startTracking = useCallback(() => {
        if (!tracker || isTracking) return;

        tracker.startTracking(5); // 每5分鐘
        setIsTracking(true);
        setStatus('GPS 追蹤已開始');
    }, [tracker, isTracking]);

    const stopTracking = useCallback(() => {
        if (!tracker || !isTracking) return;

        tracker.stopTracking();
        setIsTracking(false);
        setStatus('GPS 追蹤已停止');
    }, [tracker, isTracking]);

    const loadHistory = useCallback(async () => {
        if (!tracker) return;

        try {
            setStatus('正在載入歷史記錄...');
            const history = await tracker.getLocationHistory();
            setLocations(history.locations);
            setStatus(`載入了 ${history.total_locations} 個記錄`);
        } catch (error) {
            setStatus(`載入失敗: ${error.message}`);
        }
    }, [tracker]);

    return {
        recordLocation,
        startTracking,
        stopTracking,
        loadHistory,
        isTracking,
        locations,
        status
    };
};

// GPS 組件
const GPSComponent = ({ userId = 1 }) => {
    const {
        recordLocation,
        startTracking,
        stopTracking,
        loadHistory,
        isTracking,
        locations,
        status
    } = useGPSTracker('http://localhost:8001', userId);

    return (
        <div style={{ padding: '20px' }}>
            <h1>GPS 定位系統</h1>
            
            <div style={{ marginBottom: '20px' }}>
                <button onClick={recordLocation} style={{ margin: '5px' }}>
                    記錄當前位置
                </button>
                <button 
                    onClick={isTracking ? stopTracking : startTracking}
                    style={{ margin: '5px' }}
                >
                    {isTracking ? '停止追蹤' : '開始追蹤'}
                </button>
                <button onClick={loadHistory} style={{ margin: '5px' }}>
                    載入歷史記錄
                </button>
            </div>

            <div style={{ 
                padding: '10px', 
                backgroundColor: '#f0f0f0', 
                borderRadius: '5px',
                marginBottom: '20px' 
            }}>
                狀態: {status}
            </div>

            <h2>位置歷史 ({locations.length} 個記錄)</h2>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {locations.map(location => (
                    <div key={location.id} style={{
                        border: '1px solid #ddd',
                        margin: '5px 0',
                        padding: '10px',
                        borderRadius: '5px'
                    }}>
                        <div><strong>ID:</strong> {location.id}</div>
                        <div><strong>座標:</strong> {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}</div>
                        <div><strong>時間:</strong> {new Date(location.timestamp).toLocaleString('zh-TW')}</div>
                        <a 
                            href={`https://www.google.com/maps?q=${location.latitude},${location.longitude}`}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            在 Google Maps 中查看
                        </a>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GPSComponent;
```

## 最佳實踐

### 1. 錯誤處理
- 始終檢查瀏覽器地理定位支援
- 處理用戶拒絕定位權限的情況
- 實現網路錯誤重試機制

### 2. 效能優化
- 合理設定定位記錄頻率
- 使用節流機制避免過度請求
- 考慮在背景運行時降低記錄頻率

### 3. 隱私保護
- 明確告知用戶定位資料的使用目的
- 提供停用定位追蹤的選項
- 定期清理舊的定位資料

### 4. 使用者體驗
- 提供清晰的狀態回饋
- 允許用戶手動觸發定位記錄
- 在地圖上視覺化定位軌跡

這個整合指南提供了完整的前端 GPS 定位功能實現，可以根據實際需求進行調整和擴展。
