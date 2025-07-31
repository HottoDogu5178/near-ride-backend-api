"""
用戶頭像功能使用範例

本範例展示如何使用整合的頭像上傳功能：
1. 通過用戶更新 API 上傳頭像
2. 通過專用頭像 API 上傳頭像
3. 獲取用戶資訊（包含頭像 URL）
4. 頭像 URL 的動態構建（支援不同域名和端口）

Author: Near Ride Backend API
Date: 2024
"""

import requests
import base64
from io import BytesIO
from PIL import Image


def create_sample_avatar():
    """建立一個範例頭像圖片（Base64 格式）"""
    # 建立一個 200x200 的藍色圓形頭像
    img = Image.new('RGB', (200, 200), 'white')
    # 這裡可以添加更複雜的圖像處理
    
    # 轉換為 base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64


class AvatarExample:
    """頭像功能使用範例類別"""
    
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.user_id = 1  # 範例用戶 ID
    
    def example_1_update_user_with_avatar(self):
        """範例 1: 通過用戶更新 API 上傳頭像"""
        print("=" * 50)
        print("範例 1: 通過用戶更新 API 上傳頭像")
        print("=" * 50)
        
        url = f"{self.base_url}/users/{self.user_id}"
        
        # 準備更新資料（包含頭像）
        update_data = {
            "name": "張小明",
            "nickname": "小明",
            "avatar_base64": create_sample_avatar()
        }
        
        try:
            # 使用 PATCH 或 PUT 方法
            response = requests.patch(url, json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 用戶資料更新成功")
                print(f"   訊息: {result['message']}")
                print(f"   用戶 ID: {result['user']['id']}")
                print(f"   姓名: {result['user']['name']}")
                print(f"   暱稱: {result['user']['nickname']}")
                print(f"   頭像 URL: {result['user']['avatar_url']}")
                return result['user']['avatar_url']
            else:
                print(f"❌ 更新失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            return None
    
    def example_2_dedicated_avatar_upload(self):
        """範例 2: 使用專用頭像上傳 API"""
        print("\\n" + "=" * 50)
        print("範例 2: 使用專用頭像上傳 API")
        print("=" * 50)
        
        url = f"{self.base_url}/users/{self.user_id}/avatar"
        
        # 準備頭像資料
        avatar_data = {
            "avatar_base64": create_sample_avatar()
        }
        
        try:
            response = requests.post(url, json=avatar_data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 頭像上傳成功")
                print(f"   訊息: {result['message']}")
                print(f"   用戶 ID: {result['user_id']}")
                print(f"   頭像 URL: {result['avatar_url']}")
                return result['avatar_url']
            else:
                print(f"❌ 上傳失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            return None
    
    def example_3_get_user_info(self):
        """範例 3: 獲取用戶資訊（包含頭像）"""
        print("\\n" + "=" * 50)
        print("範例 3: 獲取用戶資訊")
        print("=" * 50)
        
        url = f"{self.base_url}/users/{self.user_id}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 用戶資訊獲取成功")
                print(f"   用戶 ID: {result['id']}")
                print(f"   Email: {result['email']}")
                print(f"   姓名: {result.get('name', 'N/A')}")
                print(f"   暱稱: {result.get('nickname', 'N/A')}")
                print(f"   頭像 URL: {result.get('avatar_url', 'N/A')}")
                print(f"   性別: {result.get('gender', 'N/A')}")
                print(f"   年齡: {result.get('age', 'N/A')}")
                print(f"   位置: {result.get('location', 'N/A')}")
                return result.get('avatar_url')
            else:
                print(f"❌ 獲取失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            return None
    
    def example_4_access_avatar_url(self, avatar_url):
        """範例 4: 訪問頭像 URL"""
        if not avatar_url:
            print("\\n⚠️  沒有可用的頭像 URL")
            return False
            
        print("\\n" + "=" * 50)
        print("範例 4: 訪問頭像 URL")
        print("=" * 50)
        
        try:
            response = requests.get(avatar_url)
            
            if response.status_code == 200:
                print("✅ 頭像訪問成功")
                print(f"   URL: {avatar_url}")
                print(f"   內容類型: {response.headers.get('content-type', 'N/A')}")
                print(f"   檔案大小: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ 訪問失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            return False
    
    def example_5_delete_avatar(self):
        """範例 5: 刪除頭像"""
        print("\\n" + "=" * 50)
        print("範例 5: 刪除頭像")
        print("=" * 50)
        
        url = f"{self.base_url}/users/{self.user_id}/avatar"
        
        try:
            response = requests.delete(url)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 頭像刪除成功")
                print(f"   訊息: {result['message']}")
                print(f"   用戶 ID: {result['user_id']}")
                return True
            else:
                print(f"❌ 刪除失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            return False


def run_examples():
    """執行所有範例"""
    print("\\n🚀 Near Ride 頭像功能使用範例")
    print("=" * 60)
    
    # 檢查服務器是否運行
    try:
        response = requests.get("http://localhost:8001/docs")
        if response.status_code != 200:
            print("❌ 服務器未啟動，請先執行：uvicorn app.main:app --host 0.0.0.0 --port 8001")
            return False
    except:
        print("❌ 無法連接到服務器，請確認服務器已在 http://localhost:8001 啟動")
        return False
    
    print("✅ 服務器連接正常")
    
    # 建立範例實例
    example = AvatarExample()
    
    # 執行範例
    avatar_url = None
    
    # 範例 1: 用戶更新含頭像
    avatar_url = example.example_1_update_user_with_avatar()
    
    # 範例 2: 專用頭像上傳
    avatar_url = example.example_2_dedicated_avatar_upload() or avatar_url
    
    # 範例 3: 獲取用戶資訊
    current_avatar = example.example_3_get_user_info()
    avatar_url = current_avatar or avatar_url
    
    # 範例 4: 訪問頭像 URL
    example.example_4_access_avatar_url(avatar_url)
    
    # 範例 5: 刪除頭像
    example.example_5_delete_avatar()
    
    print("\\n" + "=" * 60)
    print("🎉 所有範例執行完成！")
    print("=" * 60)
    
    print("\\n💡 重要說明：")
    print("- 頭像 URL 會根據請求的域名和端口動態生成")
    print("- 支援 JPEG、PNG、WEBP 格式")
    print("- 圖片會自動調整大小並優化為 WEBP 格式")
    print("- 檔案大小限制：5MB")
    print("- 最大尺寸：1024x1024")
    
    print("\\n🔗 API 端點摘要：")
    print("- PATCH/PUT /users/{user_id} - 更新用戶資料（包含頭像）")
    print("- POST /users/{user_id}/avatar - 專用頭像上傳")
    print("- GET /users/{user_id} - 獲取用戶資訊（包含頭像 URL）")
    print("- DELETE /users/{user_id}/avatar - 刪除頭像")
    print("- GET /static/avatars/{filename} - 訪問頭像檔案")


if __name__ == "__main__":
    run_examples()
