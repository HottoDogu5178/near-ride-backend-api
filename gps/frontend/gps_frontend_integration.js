/**
 * GPS 路線追蹤 API 前端整合範例
 * 本檔案示範如何在前端應用中使用 GPS 路線追蹤功能
 */

class GPSRouteAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * 上傳 GPS 路線資料
     * @param {string} userId - 用戶 ID
     * @param {string} date - 日期 (YYYY-MM-DD)
     * @param {Array} routePoints - GPS 點陣列 [{lat, lng, ts}, ...]
     * @returns {Promise} API 回應
     */
    async uploadGPSRoute(userId, date, routePoints) {
        const requestData = {
            user_id: userId,
            date: date,
            route: routePoints
        };

        try {
            const response = await fetch(`${this.baseURL}/gps/upload`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || '上傳失敗');
            }

            console.log('✅ GPS 路線上傳成功:', result);
            return result;
        } catch (error) {
            console.error('❌ GPS 路線上傳失敗:', error);
            throw error;
        }
    }

    /**
     * 獲取指定日期的 GPS 路線
     * @param {string} userId - 用戶 ID
     * @param {string} date - 日期 (YYYY-MM-DD)
     * @returns {Promise} GPS 路線資料
     */
    async getGPSRoute(userId, date) {
        try {
            const response = await fetch(`${this.baseURL}/gps/${userId}/${date}`);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || '查詢失敗');
            }

            console.log(`✅ 獲取 ${date} GPS 路線成功:`, result);
            return result;
        } catch (error) {
            console.error('❌ GPS 路線查詢失敗:', error);
            throw error;
        }
    }

    /**
     * 獲取用戶的 GPS 路線歷史
     * @param {string} userId - 用戶 ID
     * @param {number} limit - 限制返回數量 (預設 30)
     * @returns {Promise} GPS 路線歷史
     */
    async getGPSRouteHistory(userId, limit = 30) {
        try {
            const response = await fetch(`${this.baseURL}/gps/${userId}/routes?limit=${limit}`);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || '查詢失敗');
            }

            console.log(`✅ 獲取用戶 ${userId} 路線歷史成功:`, result);
            return result;
        } catch (error) {
            console.error('❌ GPS 路線歷史查詢失敗:', error);
            throw error;
        }
    }

    /**
     * 刪除指定日期的 GPS 路線
     * @param {string} userId - 用戶 ID
     * @param {string} date - 日期 (YYYY-MM-DD)
     * @returns {Promise} 刪除結果
     */
    async deleteGPSRoute(userId, date) {
        try {
            const response = await fetch(`${this.baseURL}/gps/${userId}/${date}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || '刪除失敗');
            }

            console.log(`✅ 刪除 ${date} GPS 路線成功:`, result);
            return result;
        } catch (error) {
            console.error('❌ GPS 路線刪除失敗:', error);
            throw error;
        }
    }
}

/**
 * GPS 位置追蹤管理器
 * 負責收集用戶的 GPS 位置並上傳到後端
 */
class GPSTracker {
    constructor(apiClient, userId) {
        this.api = apiClient;
        this.userId = userId;
        this.currentRoute = [];
        this.isTracking = false;
        this.watchId = null;
        this.trackingInterval = 30000; // 30 秒記錄一次位置
    }

    /**
     * 開始 GPS 追蹤
     */
    startTracking() {
        if (this.isTracking) {
            console.log('GPS 追蹤已在進行中');
            return;
        }

        if (!navigator.geolocation) {
            throw new Error('此瀏覽器不支援地理位置功能');
        }

        console.log('🛰️ 開始 GPS 追蹤...');
        this.isTracking = true;
        this.currentRoute = [];

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        this.watchId = navigator.geolocation.watchPosition(
            (position) => this.handlePositionUpdate(position),
            (error) => this.handlePositionError(error),
            options
        );
    }

    /**
     * 停止 GPS 追蹤
     */
    stopTracking() {
        if (!this.isTracking) {
            console.log('GPS 追蹤未在進行中');
            return;
        }

        console.log('🛑 停止 GPS 追蹤');
        this.isTracking = false;

        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }

    /**
     * 處理位置更新
     * @param {Position} position 
     */
    handlePositionUpdate(position) {
        const { latitude, longitude } = position.coords;
        const timestamp = new Date().toISOString();

        const gpsPoint = {
            lat: latitude,
            lng: longitude,
            ts: timestamp
        };

        this.currentRoute.push(gpsPoint);
        console.log(`📍 新增 GPS 點: ${latitude}, ${longitude} at ${timestamp}`);

        // 觸發自定義事件
        this.dispatchPositionEvent(gpsPoint);
    }

    /**
     * 處理位置錯誤
     * @param {PositionError} error 
     */
    handlePositionError(error) {
        let errorMessage = '';
        switch (error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = '用戶拒絕了地理位置請求';
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = '無法獲取位置資訊';
                break;
            case error.TIMEOUT:
                errorMessage = '獲取位置資訊超時';
                break;
            default:
                errorMessage = '獲取位置時發生未知錯誤';
        }
        console.error('❌ GPS 追蹤錯誤:', errorMessage);
    }

    /**
     * 上傳當天的路線資料
     * @param {string} date - 日期 (YYYY-MM-DD)，預設為今天
     */
    async uploadRoute(date = null) {
        if (this.currentRoute.length === 0) {
            throw new Error('沒有路線資料可上傳');
        }

        const uploadDate = date || new Date().toISOString().split('T')[0];

        try {
            const result = await this.api.uploadGPSRoute(
                this.userId,
                uploadDate,
                this.currentRoute
            );
            
            console.log(`✅ 路線上傳成功: ${result.point_count} 個點`);
            return result;
        } catch (error) {
            console.error('❌ 路線上傳失敗:', error);
            throw error;
        }
    }

    /**
     * 清除當前路線資料
     */
    clearCurrentRoute() {
        this.currentRoute = [];
        console.log('🗑️ 已清除當前路線資料');
    }

    /**
     * 獲取當前路線資料
     */
    getCurrentRoute() {
        return [...this.currentRoute];
    }

    /**
     * 觸發位置更新事件
     * @param {Object} gpsPoint 
     */
    dispatchPositionEvent(gpsPoint) {
        const event = new CustomEvent('gpsPositionUpdate', {
            detail: gpsPoint
        });
        document.dispatchEvent(event);
    }
}

// 使用範例
async function initGPSTracking() {
    const userId = "1"; // 替換為實際的用戶 ID
    const gpsAPI = new GPSRouteAPI();
    const tracker = new GPSTracker(gpsAPI, userId);

    // 監聽位置更新事件
    document.addEventListener('gpsPositionUpdate', (event) => {
        const { lat, lng, ts } = event.detail;
        console.log(`📱 位置更新: ${lat}, ${lng} at ${ts}`);
        
        // 在這裡可以更新 UI，例如在地圖上顯示新位置
        updateMapLocation(lat, lng);
    });

    try {
        // 開始追蹤
        tracker.startTracking();

        // 模擬運行一段時間後上傳資料
        setTimeout(async () => {
            try {
                await tracker.uploadRoute();
                console.log('路線已自動上傳');
            } catch (error) {
                console.error('自動上傳失敗:', error);
            }
        }, 60000); // 1 分鐘後上傳

        // 查詢歷史路線
        const history = await gpsAPI.getGPSRouteHistory(userId, 10);
        console.log('📊 路線歷史:', history);

    } catch (error) {
        console.error('GPS 追蹤初始化失敗:', error);
    }
}

// 地圖更新函數 (需要根據實際使用的地圖庫實作)
function updateMapLocation(lat, lng) {
    // 這裡實作地圖位置更新邏輯
    // 例如使用 Google Maps, Leaflet, 或其他地圖庫
    console.log(`🗺️ 更新地圖位置: ${lat}, ${lng}`);
}

// 測試數據範例
const testGPSData = {
    userId: "1",
    date: "2025-01-31",
    route: [
        {
            lat: 25.047924,
            lng: 121.517081,
            ts: "2025-01-31T08:30:00.000Z"
        },
        {
            lat: 25.046500,
            lng: 121.516800,
            ts: "2025-01-31T08:32:00.000Z"
        },
        {
            lat: 25.045200,
            lng: 121.516200,
            ts: "2025-01-31T08:34:00.000Z"
        },
        {
            lat: 25.044100,
            lng: 121.515500,
            ts: "2025-01-31T08:36:00.000Z"
        },
        {
            lat: 25.034000,
            lng: 121.564500,
            ts: "2025-01-31T08:45:00.000Z"
        }
    ]
};

// 測試函數
async function testGPSAPI() {
    const gpsAPI = new GPSRouteAPI();
    
    try {
        // 測試上傳
        console.log('🧪 測試上傳 GPS 資料...');
        const uploadResult = await gpsAPI.uploadGPSRoute(
            testGPSData.userId,
            testGPSData.date,
            testGPSData.route
        );

        // 測試查詢
        console.log('🧪 測試查詢 GPS 資料...');
        const routeData = await gpsAPI.getGPSRoute(
            testGPSData.userId,
            testGPSData.date
        );

        // 測試歷史查詢
        console.log('🧪 測試查詢歷史資料...');
        const historyData = await gpsAPI.getGPSRouteHistory(testGPSData.userId);

        console.log('✅ 所有測試通過！');

    } catch (error) {
        console.error('❌ 測試失敗:', error);
    }
}

// 導出供其他模組使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GPSRouteAPI, GPSTracker };
}
