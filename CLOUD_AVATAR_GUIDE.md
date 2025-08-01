"""
雲端頭像服務使用指南

本檔案說明如何在不同環境下使用頭像服務
"""

# ===== 1. 開發環境設定 =====

# 在開發環境中，不設定環境變數會自動使用本地儲存
# 適用於快速開發和測試

print("開發環境使用方式：")
print("1. 不需要設定任何環境變數")
print("2. 圖片會儲存在 uploads/avatars/ 或 /tmp/avatars/")
print("3. 重啟伺服器後圖片仍會保留（本地開發）")

# ===== 2. 生產環境設定 (Cloudinary) =====

# 在生產環境（如 Render）設定環境變數：
production_env_vars = """
# 在 Render Dashboard 或 .env 檔案中設定：
USE_CLOUD_STORAGE=true
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# 替換為您的 Cloudinary 憑證：
# api_key: 從 Cloudinary Dashboard 獲取
# api_secret: 從 Cloudinary Dashboard 獲取  
# cloud_name: 您的 Cloudinary 雲端名稱
"""

print("\n生產環境設定：")
print(production_env_vars)

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
