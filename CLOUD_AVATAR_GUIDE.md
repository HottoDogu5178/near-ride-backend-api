# 雲端頭像服務使用指南

本檔案說明如何在不同環境下使用頭像服務

## 🚀 部署解決方案

### 方案 1：Cloudinary（推薦）
如果 Cloudinary 在 Render 上安裝順利：

```bash
# Render 環境變數
USE_CLOUD_STORAGE=true
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

### 方案 2：Imgur（備用方案）
如果 Cloudinary 安裝有問題：

```python
# 在 user_routes.py 中替換匯入
from app.services.avatar_service_simple import simple_avatar_service as avatar_service

# Render 環境變數
IMGUR_CLIENT_ID=your_imgur_client_id
```

### 方案 3：純本地儲存（開發用）
不設定任何環境變數，使用本地儲存。

## 📋 Render 部署建議

### 1. 更新的 render.yaml
```yaml
services:
  - type: web
    name: near-ride-backend
    runtime: python
    env: python
    buildCommand: |
      pip install --upgrade pip setuptools wheel
      pip install --no-cache-dir --only-binary=all -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: USE_CLOUD_STORAGE
        value: "true"
```

### 2. 更新的 requirements.txt
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-multipart==0.0.6
pillow==10.1.0
pydantic==2.5.0
cloudinary==1.40.0  # 使用更新版本
requests==2.31.0    # 用於 Imgur 備用方案
```

# ===== 3. API 使用範例 =====

api_examples = """
# 上傳頭像 (通過用戶更新)
curl -X PATCH "https://your-app.onrender.com/users/1" \\
  -H "Content-Type: application/json" \\
  -d '{
    "nickname": "用戶暱稱",
    "avatar_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
  }'

# 專用頭像上傳
curl -X POST "https://your-app.onrender.com/users/1/avatar" \\
  -H "Content-Type: application/json" \\
  -d '{
    "avatar_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
  }'

# 刪除頭像
curl -X DELETE "https://your-app.onrender.com/users/1/avatar"

# 獲取用戶資訊（包含頭像 URL）
curl -X GET "https://your-app.onrender.com/users/1"
"""

print("\nAPI 使用範例：")
print(api_examples)

# ===== 4. 功能特性說明 =====

features = """
✅ 自動環境切換
   - 開發環境：本地儲存
   - 生產環境：Cloudinary 雲端儲存

✅ 圖片處理
   - 支援 JPEG、PNG、WEBP 格式
   - 自動調整大小（最大 1024x1024）
   - 自動優化為 WEBP 格式
   - 檔案大小限制：5MB

✅ 安全性
   - Base64 資料驗證
   - 圖片格式檢查
   - 檔案大小限制
   - 安全檔案命名

✅ 錯誤處理
   - 完整的錯誤訊息
   - 自動回退機制
   - 日誌記錄

✅ 效能優化
   - CDN 加速（Cloudinary）
   - 圖片壓縮
   - 智能快取
"""

print("\n功能特性：")
print(features)

# ===== 5. 疑難排解 =====

troubleshooting = """
常見問題解決：

1. "Cloudinary 套件未安裝"
   解決：pip install cloudinary==1.36.0

2. "雲端上傳失敗"
   檢查：
   - CLOUDINARY_URL 環境變數是否正確
   - 網路連線是否正常
   - Cloudinary 帳號配額是否充足

3. "圖片檔案過大"
   解決：
   - 壓縮圖片後再上傳
   - 檢查檔案大小（限制：5MB）

4. "不支援的格式"
   解決：
   - 使用 JPEG、PNG 或 WEBP 格式
   - 檢查 base64 資料是否正確

5. 在 Render 上圖片遺失
   原因：使用本地儲存，重啟後會遺失
   解決：設定 Cloudinary 環境變數
"""

print("\n疑難排解：")
print(troubleshooting)

if __name__ == "__main__":
    print("=" * 60)
    print("🎉 雲端頭像服務已就緒！")
    print("=" * 60)
    print("請根據您的部署環境選擇適當的設定方式。")
