# Near Ride Backend API

一個基於 FastAPI 的後端 API 服務，提供用戶管理、GPS 路線追蹤、聊天、朋友關係和興趣愛好管理功能。

## 🚀 快速開始

### 環境需求
- Python 3.11+
- PostgreSQL 資料庫

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 啟動服務
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 執行測試
```bash
python test_comprehensive.py
```

## 📁 專案結構

```
near-ride-backend-api/
├── app/
│   ├── models/          # 資料庫模型
│   ├── routes/          # API 路由
│   ├── services/        # 業務邏輯服務
│   ├── database.py      # 資料庫配置
│   └── main.py          # 應用程式入口
├── test_comprehensive.py   # 綜合測試
├── gps_frontend_integration.js  # 前端整合範例
├── GPS_API_Documentation.md     # GPS API 文檔
└── requirements.txt     # Python 依賴
```

## 🔧 主要功能

### 用戶管理
- 用戶註冊、登入、資料更新
- 用戶資料查詢和管理

### GPS 路線追蹤
- GPS 路線資料上傳和儲存
- 歷史路線查詢和管理
- 支援 JSON 格式路線資料

### 聊天功能
- 即時聊天訊息
- WebSocket 支援

### 朋友關係
- 朋友邀請和管理
- 附近用戶搜尋

### 興趣愛好
- 用戶興趣標籤管理
- 興趣匹配功能

## 🌐 API 端點

### 用戶 API
- `POST /users/` - 創建用戶
- `GET /users/{id}` - 查詢用戶
- `PUT /users/{id}` - 更新用戶
- `DELETE /users/{id}` - 刪除用戶

### GPS API
- `POST /gps/upload` - 上傳 GPS 路線
- `GET /gps/{user_id}/{date}` - 查詢指定日期路線
- `GET /gps/{user_id}/routes` - 查詢路線歷史
- `DELETE /gps/{user_id}/{date}` - 刪除路線

### 其他 API
請參考各模組的路由文件或 API 文檔。

## 🗄️ 資料庫

使用 PostgreSQL 資料庫，透過 SQLAlchemy ORM 進行資料存取。

主要資料表：
- `users` - 用戶資料
- `gps_routes` - GPS 路線資料
- `gps_points` - GPS 點位資料
- `chat_messages` - 聊天訊息
- `user_status` - 用戶狀態
- `hobbies` - 興趣愛好

## 🧪 測試

執行綜合測試：
```bash
python test_comprehensive.py
```

測試包含：
- 伺服器連接測試
- GPS 功能測試
- 用戶管理測試

## 📝 授權

本專案僅供學習和開發使用。
