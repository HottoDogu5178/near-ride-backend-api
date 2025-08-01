"""
測試雲端頭像服務的基本功能
"""

import os
import sys
import base64
from io import BytesIO
from PIL import Image

# 添加專案路徑
sys.path.append('/Users/ianliu/Documents/VScode/near ride backend api')

def create_test_image():
    """創建測試圖片的 base64 資料"""
    # 創建一個 100x100 的紅色正方形
    img = Image.new('RGB', (100, 100), color='red')
    
    # 轉換為 base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64

def test_avatar_service():
    """測試頭像服務"""
    print("🧪 測試雲端頭像服務")
    print("=" * 40)
    
    try:
        from app.services.avatar_service import cloud_avatar_service
        
        print("✅ 成功匯入 cloud_avatar_service")
        print(f"   雲端儲存啟用: {cloud_avatar_service.use_cloud_storage}")
        print(f"   Cloudinary URL: {'已設定' if cloud_avatar_service.cloudinary_url else '未設定'}")
        
        # 測試圖片驗證
        test_image_base64 = create_test_image()
        
        try:
            image = cloud_avatar_service.validate_base64_image(test_image_base64)
            print("✅ 圖片驗證成功")
            print(f"   圖片格式: {image.format}")
            print(f"   圖片尺寸: {image.size}")
        except Exception as e:
            print(f"❌ 圖片驗證失敗: {e}")
        
        # 測試圖片處理
        try:
            processed_image = cloud_avatar_service.process_avatar_image(image)
            print("✅ 圖片處理成功")
            print(f"   處理後大小: {len(processed_image.getvalue())} bytes")
        except Exception as e:
            print(f"❌ 圖片處理失敗: {e}")
        
        print("\n🎯 基本功能測試完成")
        
    except ImportError as e:
        print(f"❌ 匯入失敗: {e}")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

def test_environment_variables():
    """測試環境變數"""
    print("\n🔍 檢查環境變數")
    print("=" * 40)
    
    use_cloud = os.getenv('USE_CLOUD_STORAGE', 'false')
    cloudinary_url = os.getenv('CLOUDINARY_URL', '未設定')
    
    print(f"USE_CLOUD_STORAGE: {use_cloud}")
    print(f"CLOUDINARY_URL: {'已設定' if cloudinary_url != '未設定' else '未設定'}")
    
    if use_cloud.lower() == 'true' and cloudinary_url != '未設定':
        print("✅ 雲端儲存配置完整")
    else:
        print("⚠️ 雲端儲存配置不完整，將使用本地儲存")

if __name__ == "__main__":
    test_environment_variables()
    test_avatar_service()
