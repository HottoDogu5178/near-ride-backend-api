# Near Ride 用戶頭像功能完整實現

## 🎯 功能概述

本實現提供了完整的用戶頭像管理功能，支援 base64 圖片上傳、自動圖片處理、動態 URL 生成等特性。頭像功能已完全整合到用戶資料格式中，使用相同的 HTTP 端口提供服務。

## ✨ 主要特性

### 🖼️ 圖片處理
- **支援格式**: JPEG、PNG、WEBP
- **自動最佳化**: 轉換為 WEBP 格式以減少檔案大小
- **尺寸調整**: 自動調整至最大 1024x1024，保持長寬比
- **檔案大小限制**: 最大 5MB
- **背景處理**: 透明背景自動轉換為白色背景

### 🌐 動態 URL 生成
- **域名適應**: 根據請求的域名和端口動態生成頭像 URL
- **跨環境支援**: 開發、測試、生產環境無需修改程式碼
- **安全檔案服務**: 包含檔案存在驗證和安全檢查

### 🔗 API 整合
- **統一端點**: 頭像功能整合在用戶資料更新 API 中
- **多種上傳方式**: 支援專用頭像 API 和用戶更新 API
- **完整 CRUD**: 支援創建、讀取、更新、刪除操作

## 📁 檔案結構

```
app/
├── services/
│   └── avatar_service.py          # 頭像處理核心服務
├── routes/
│   ├── user_routes.py            # 用戶路由（包含頭像功能）
│   └── static_routes.py          # 靜態檔案服務路由
├── models/
│   └── user.py                   # 用戶模型（包含 avatar_url 欄位）
└── main.py                       # 主應用程序

uploads/
└── avatars/                      # 頭像檔案儲存目錄

# 測試和範例檔案
test_avatar_upload.py             # 完整測試套件
avatar_usage_examples.py          # 使用範例
```

## 🛠️ 核心組件

### 1. AvatarService 類別 (`app/services/avatar_service.py`)

```python
class AvatarService:
    def __init__(self, upload_dir: str = "uploads/avatars", base_url: Optional[str] = None):
        # 初始化服務，支援動態 URL 配置
    
    def save_avatar(self, avatar_base64: str, user_id: int, request_url: Optional[str] = None) -> str:
        # 儲存 base64 格式頭像，返回公開 URL
    
    def validate_base64_image(self, base64_data: str) -> Image.Image:
        # 驗證並解析 base64 圖片資料
    
    def process_avatar_image(self, image: Image.Image) -> Image.Image:
        # 處理圖片（調整大小、格式轉換等）
    
    def delete_avatar(self, avatar_url: str) -> bool:
        # 刪除頭像檔案
```

### 2. API 端點

#### 用戶資料更新（包含頭像）
```http
PATCH/PUT /users/{user_id}
Content-Type: application/json

{
    "name": "張小明",
    "nickname": "小明",
    "avatar_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### 專用頭像上傳
```http
POST /users/{user_id}/avatar
Content-Type: application/json

{
    "avatar_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### 獲取用戶資訊
```http
GET /users/{user_id}

回應：
{
    "id": 1,
    "email": "user@example.com",
    "name": "張小明",
    "nickname": "小明",
    "avatar_url": "http://localhost:8001/static/avatars/avatar_1_abc123.webp",
    ...
}
```

#### 刪除頭像
```http
DELETE /users/{user_id}/avatar
```

#### 訪問頭像檔案
```http
GET /static/avatars/{filename}
```

## 🚀 使用方式

### 1. 基本頭像上傳（透過用戶更新）

```python
import requests
import base64

# 準備圖片資料
with open("avatar.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

# 更新用戶資料（包含頭像）
response = requests.patch(
    "http://localhost:8001/users/1",
    json={
        "name": "張小明",
        "avatar_base64": img_base64
    }
)

result = response.json()
avatar_url = result['user']['avatar_url']
print(f"頭像 URL: {avatar_url}")
```

### 2. 專用頭像上傳 API

```python
# 使用專用 API 上傳頭像
response = requests.post(
    "http://localhost:8001/users/1/avatar",
    json={"avatar_base64": img_base64}
)

result = response.json()
avatar_url = result['avatar_url']
```

### 3. 獲取用戶頭像資訊

```python
# 獲取用戶資訊
response = requests.get("http://localhost:8001/users/1")
user_info = response.json()
avatar_url = user_info.get('avatar_url')

if avatar_url:
    # 下載頭像檔案
    avatar_response = requests.get(avatar_url)
    with open("downloaded_avatar.webp", "wb") as f:
        f.write(avatar_response.content)
```

## 🧪 測試

### 執行完整測試套件
```bash
python test_avatar_upload.py
```

### 執行使用範例
```bash
python avatar_usage_examples.py
```

### 測試覆蓋範圍
- ✅ 基本頭像上傳功能
- ✅ 用戶更新 API 整合
- ✅ 大圖片處理（自動調整大小）
- ✅ 無效圖片檢測
- ✅ 頭像檔案訪問
- ✅ 頭像刪除功能
- ✅ 動態 URL 生成

## 🔧 配置選項

### AvatarService 配置
```python
avatar_service = AvatarService(
    upload_dir="uploads/avatars",    # 檔案儲存目錄
    base_url=None                    # 基礎 URL（None 表示動態生成）
)
```

### 圖片處理參數
- `max_size`: 1024 (最大寬度/高度)
- `max_file_size`: 5MB (最大檔案大小)
- `allowed_formats`: ['JPEG', 'PNG', 'WEBP']
- `output_quality`: 85 (WEBP 品質)

## 🌍 部署注意事項

### 1. 檔案儲存目錄
確保 `uploads/avatars/` 目錄具有適當的寫入權限：
```bash
mkdir -p uploads/avatars
chmod 755 uploads/avatars
```

### 2. 靜態檔案服務
頭像檔案透過 `/static/avatars/` 端點提供服務，無需額外的 Web 服務器配置。

### 3. 環境變數（可選）
```env
AVATAR_UPLOAD_DIR=uploads/avatars
AVATAR_BASE_URL=https://yourapp.com
AVATAR_MAX_SIZE=1024
AVATAR_MAX_FILE_SIZE=5242880
```

## 🚨 錯誤處理

### 常見錯誤碼
- `400`: 無效的圖片資料、格式不支援、檔案過大
- `404`: 用戶不存在、頭像檔案不存在
- `500`: 伺服器內部錯誤（檔案系統問題等）

### 錯誤回應格式
```json
{
    "detail": "頭像處理失敗: 圖片檔案過大：6291456 位元組，最大允許：5242880 位元組"
}
```

## 📈 性能特性

### 1. 圖片最佳化
- 自動轉換為 WEBP 格式（平均節省 25-35% 檔案大小）
- 智能尺寸調整（保持長寬比）
- 品質最佳化（平衡檔案大小與視覺品質）

### 2. 記憶體效率
- 串流處理大圖片
- 自動記憶體清理
- 限制同時處理的圖片數量

### 3. 快取支援
- 靜態檔案適當的 HTTP 快取頭
- 支援條件請求（ETag）

## 🔒 安全性考量

### 1. 檔案驗證
- 嚴格的圖片格式檢查
- Base64 資料驗證
- 檔案大小限制

### 2. 路徑安全
- 檔案名稱隨機生成
- 禁止路徑遍歷攻擊
- 安全的檔案存取檢查

### 3. 輸入清理
- Base64 資料清理
- 移除潛在惡意 metadata
- 圖片重新處理（移除 EXIF 等）

## 🎉 完成狀態

✅ **核心功能**: 完全實現  
✅ **API 整合**: 完全整合到用戶資料格式  
✅ **動態 URL**: 支援不同環境自動適應  
✅ **圖片處理**: 自動最佳化和格式轉換  
✅ **錯誤處理**: 完整的錯誤檢測和回應  
✅ **測試覆蓋**: 7/7 測試通過  
✅ **文件**: 完整的使用說明和範例  

---

**🚀 系統已準備就緒，可以投入生產使用！**
