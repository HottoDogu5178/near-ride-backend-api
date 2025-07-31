"""
頭像上傳功能測試

測試用戶頭像的上傳、更新和刪除功能
"""

import requests
import base64
import json
from io import BytesIO
from PIL import Image
import sys
import os

# 將父目錄加入 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 測試設定
BASE_URL = "http://localhost:8001"
TEST_USER_ID = 1

def create_test_image() -> str:
    """
    創建測試用的 base64 圖片
    
    Returns:
        str: base64 編碼的圖片資料
    """
    # 創建一個簡單的測試圖片（100x100 紅色正方形）
    image = Image.new('RGB', (100, 100), color='red')
    
    # 轉換為 base64
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    
    base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_data

def create_large_test_image() -> str:
    """
    創建大尺寸測試圖片
    
    Returns:
        str: base64 編碼的大圖片資料
    """
    # 創建一個大圖片（2000x2000）
    image = Image.new('RGB', (2000, 2000), color='blue')
    
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    
    base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_data

class TestAvatarUpload:
    """頭像上傳測試類別"""
    
    @staticmethod
    def test_server_connection():
        """測試服務器連接"""
        try:
            response = requests.get(f"{BASE_URL}/docs")
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def test_upload_avatar():
        """測試頭像上傳"""
        url = f"{BASE_URL}/users/{TEST_USER_ID}/avatar"
        
        try:
            # 創建測試圖片
            test_image_base64 = create_test_image()
            
            upload_data = {
                "avatar_base64": test_image_base64
            }
            
            response = requests.post(url, json=upload_data)
            
            print(f"✓ 頭像上傳 - 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  成功上傳頭像: {result['avatar_url']}")
                print(f"  用戶 ID: {result['user_id']}")
                return result['avatar_url']
            else:
                print(f"  錯誤回應: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 頭像上傳失敗: {e}")
            return None
    
    @staticmethod
    def test_update_user_with_avatar():
        """測試透過用戶更新 API 上傳頭像"""
        url = f"{BASE_URL}/users/{TEST_USER_ID}"
        
        try:
            # 創建測試圖片
            test_image_base64 = create_test_image()
            
            update_data = {
                "nickname": "頭像測試用戶",
                "avatar_base64": test_image_base64
            }
            
            response = requests.patch(url, json=update_data)
            
            print(f"✓ 用戶更新含頭像 - 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                # 修正：使用正確的回應結構
                user_data = result.get('user', {})
                print(f"  用戶暱稱: {user_data.get('nickname', 'N/A')}")
                print(f"  頭像 URL: {user_data.get('avatar_url', 'N/A')}")
                return user_data.get('avatar_url')
            else:
                print(f"  錯誤回應: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 用戶更新失敗: {e}")
            return None
    
    @staticmethod
    def test_get_user_info():
        """測試獲取用戶資訊（包含頭像）"""
        url = f"{BASE_URL}/users/{TEST_USER_ID}"
        
        try:
            response = requests.get(url)
            
            print(f"✓ 獲取用戶資訊 - 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  用戶 ID: {result['id']}")
                print(f"  Email: {result['email']}")
                print(f"  暱稱: {result.get('nickname', 'N/A')}")
                print(f"  頭像: {result.get('avatar_url', 'N/A')}")
                return result.get('avatar_url')
            else:
                print(f"  錯誤回應: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 獲取用戶資訊失敗: {e}")
            return None
    
    @staticmethod
    def test_access_avatar_url(avatar_url):
        """測試訪問頭像 URL"""
        if not avatar_url:
            print("❌ 沒有頭像 URL 可測試")
            return False
        
        try:
            response = requests.get(avatar_url)
            
            print(f"✓ 訪問頭像 URL - 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                print(f"  內容類型: {content_type}")
                print(f"  檔案大小: {content_length} bytes")
                return True
            else:
                print(f"  無法訪問頭像: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 訪問頭像 URL 失敗: {e}")
            return False
    
    @staticmethod
    def test_large_image_upload():
        """測試大圖片上傳（應該被自動縮放）"""
        url = f"{BASE_URL}/users/{TEST_USER_ID}/avatar"
        
        try:
            # 創建大尺寸測試圖片
            large_image_base64 = create_large_test_image()
            
            upload_data = {
                "avatar_base64": large_image_base64
            }
            
            response = requests.post(url, json=upload_data)
            
            print(f"✓ 大圖片上傳 - 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  大圖片成功上傳並處理: {result['avatar_url']}")
                return result['avatar_url']
            else:
                print(f"  大圖片上傳失敗: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 大圖片上傳測試失敗: {e}")
            return None
    
    @staticmethod
    def test_invalid_image_upload():
        """測試無效圖片上傳"""
        url = f"{BASE_URL}/users/{TEST_USER_ID}/avatar"
        
        try:
            # 使用無效的 base64 資料
            invalid_data = {
                "avatar_base64": "invalid_base64_data"
            }
            
            response = requests.post(url, json=invalid_data)
            
            print(f"✓ 無效圖片上傳測試 - 狀態碼: {response.status_code}")
            
            if response.status_code == 400:
                print(f"  正確拒絕無效圖片: {response.json().get('detail', '')}")
                return True
            else:
                print(f"  預期錯誤狀態碼 400，實際: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 無效圖片測試失敗: {e}")
            return False
    
    @staticmethod
    def test_delete_avatar():
        """測試刪除頭像"""
        url = f"{BASE_URL}/users/{TEST_USER_ID}/avatar"
        
        try:
            response = requests.delete(url)
            
            print(f"✓ 刪除頭像 - 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  {result['message']}")
                return True
            else:
                print(f"  刪除失敗: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 刪除頭像失敗: {e}")
            return False

def run_avatar_tests():
    """執行所有頭像相關測試"""
    print("=" * 60)
    print("頭像上傳功能測試開始")
    print("=" * 60)
    
    # 檢查服務器連接
    if not TestAvatarUpload.test_server_connection():
        print("❌ 無法連接到服務器，請確認服務器已在 http://localhost:8001 啟動")
        return False
    
    print("✓ 服務器連接正常")
    print()
    
    # 執行測試
    tests = [
        ("專用頭像上傳 API", TestAvatarUpload.test_upload_avatar),
        ("獲取用戶資訊", TestAvatarUpload.test_get_user_info),
        ("通過用戶更新上傳頭像", TestAvatarUpload.test_update_user_with_avatar),
        ("大圖片上傳測試", TestAvatarUpload.test_large_image_upload),
        ("無效圖片上傳測試", TestAvatarUpload.test_invalid_image_upload)
    ]
    
    passed = 0
    failed = 0
    avatar_url = None
    
    for test_name, test_func in tests:
        print(f"\n📷 測試: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} - 通過")
                passed += 1
                # 保存頭像 URL 用於後續測試
                if isinstance(result, str) and result.startswith('http'):
                    avatar_url = result
            else:
                print(f"❌ {test_name} - 失敗")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} - 錯誤: {e}")
            failed += 1
    
    # 測試頭像 URL 訪問（在刪除之前）
    if avatar_url:
        print(f"\n📷 測試: 頭像 URL 訪問")
        print("-" * 40)
        if TestAvatarUpload.test_access_avatar_url(avatar_url):
            print(f"✅ 頭像 URL 訪問 - 通過")
            passed += 1
        else:
            print(f"❌ 頭像 URL 訪問 - 失敗")
            failed += 1
    
    # 最後測試頭像刪除
    print(f"\n📷 測試: 刪除頭像")
    print("-" * 40)
    try:
        result = TestAvatarUpload.test_delete_avatar()
        if result:
            print(f"✅ 刪除頭像 - 通過")
            passed += 1
        else:
            print(f"❌ 刪除頭像 - 失敗")
            failed += 1
    except Exception as e:
        print(f"❌ 刪除頭像 - 錯誤: {e}")
        failed += 1
        if TestAvatarUpload.test_access_avatar_url(avatar_url):
            print(f"✅ 頭像 URL 訪問 - 通過")
            passed += 1
        else:
            print(f"❌ 頭像 URL 訪問 - 失敗")
            failed += 1
    
    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    print(f"✅ 通過: {passed}")
    print(f"❌ 失敗: {failed}")
    print(f"📊 總計: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有頭像功能測試都通過了！")
        return True
    else:
        print(f"\n⚠️  有 {failed} 個測試失敗，請檢查系統配置。")
        return False

if __name__ == "__main__":
    success = run_avatar_tests()
    exit(0 if success else 1)
