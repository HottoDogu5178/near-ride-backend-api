#!/usr/bin/env python3
"""
Near Ride Backend API 測試套件
包含所有 API 端點的綜合測試
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """測試基本連接"""
        print("🔗 測試伺服器連接...")
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ 伺服器連接正常")
                return True
            else:
                print(f"❌ 伺服器回應異常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 無法連接到伺服器: {e}")
            return False

    def test_gps_functionality(self):
        """測試 GPS 路線追蹤功能"""
        print("\n🛣️ 測試 GPS 路線追蹤功能...")
        
        user_id = "1"
        test_date = datetime.now().strftime("%Y-%m-%d")
        
        # 測試資料
        test_route_data = {
            "user_id": user_id,
            "date": test_date,
            "route": [
                {"lat": 25.0478, "lng": 121.5173, "ts": f"{test_date}T08:30:00.000Z"},
                {"lat": 25.0465, "lng": 121.5168, "ts": f"{test_date}T08:32:00.000Z"},
                {"lat": 25.0452, "lng": 121.5162, "ts": f"{test_date}T08:34:00.000Z"},
                {"lat": 25.0340, "lng": 121.5645, "ts": f"{test_date}T08:45:00.000Z"}
            ]
        }
        
        try:
            # 1. 上傳 GPS 路線
            print("📤 測試上傳 GPS 路線...")
            response = self.session.post(f"{self.base_url}/gps/upload", json=test_route_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 上傳成功: {result['point_count']} 個點")
            else:
                print(f"❌ 上傳失敗: {response.text}")
                return False
            
            # 2. 查詢路線
            print("📥 測試查詢路線...")
            response = self.session.get(f"{self.base_url}/gps/{user_id}/{test_date}")
            if response.status_code == 200:
                route_data = response.json()
                print(f"✅ 查詢成功: {len(route_data['route'])} 個點")
            else:
                print(f"❌ 查詢失敗: {response.text}")
                return False
            
            # 3. 查詢歷史
            print("📋 測試查詢歷史...")
            response = self.session.get(f"{self.base_url}/gps/{user_id}/routes?limit=5")
            if response.status_code == 200:
                history = response.json()
                print(f"✅ 歷史查詢成功: {len(history)} 條記錄")
            else:
                print(f"❌ 歷史查詢失敗: {response.text}")
                return False
            
            # 4. 刪除路線
            print("🗑️ 測試刪除路線...")
            response = self.session.delete(f"{self.base_url}/gps/{user_id}/{test_date}")
            if response.status_code == 200:
                print("✅ 刪除成功")
            else:
                print(f"❌ 刪除失敗: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ GPS 測試發生錯誤: {e}")
            return False

    def test_user_functionality(self):
        """測試用戶管理功能"""
        print("\n👤 測試用戶管理功能...")
        
        # 測試資料
        test_user_data = {
            "name": "測試用戶",
            "email": "test@example.com",
            "password": "testpassword123",
            "age": 25
        }
        
        try:
            # 測試創建用戶
            print("📝 測試創建用戶...")
            response = self.session.post(f"{self.base_url}/users/", json=test_user_data)
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get('id')
                print(f"✅ 用戶創建成功: ID {user_id}")
                
                # 測試查詢用戶
                print("🔍 測試查詢用戶...")
                response = self.session.get(f"{self.base_url}/users/{user_id}")
                if response.status_code == 200:
                    print("✅ 用戶查詢成功")
                else:
                    print(f"❌ 用戶查詢失敗: {response.text}")
                    return False
                
                return True
            else:
                print(f"❌ 用戶創建失敗: {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ 用戶測試發生錯誤: {e}")
            return False

    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始 Near Ride Backend API 綜合測試...")
        print(f"目標伺服器: {self.base_url}")
        
        # 檢查連接
        if not self.test_connection():
            print("❌ 無法連接伺服器，測試終止")
            return False
        
        # 執行各項測試
        gps_passed = self.test_gps_functionality()
        user_passed = self.test_user_functionality()
        
        # 總結
        print("\n📊 測試總結:")
        print(f"GPS 功能: {'✅ 通過' if gps_passed else '❌ 失敗'}")
        print(f"用戶功能: {'✅ 通過' if user_passed else '❌ 失敗'}")
        
        if gps_passed and user_passed:
            print("\n🎉 所有測試通過！系統運行正常")
            return True
        else:
            print("\n⚠️ 部分測試失敗，請檢查系統狀態")
            return False

def main():
    """主程式"""
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n📋 API 端點列表:")
        print("用戶管理:")
        print("• POST /users/           - 創建用戶")
        print("• GET  /users/{id}       - 查詢用戶")
        print("• PUT  /users/{id}       - 更新用戶")
        print("• DELETE /users/{id}     - 刪除用戶")
        print("\nGPS 路線:")
        print("• POST /gps/upload              - 上傳路線")
        print("• GET  /gps/{user_id}/{date}    - 查詢指定日期路線")
        print("• GET  /gps/{user_id}/routes    - 查詢路線歷史")
        print("• DELETE /gps/{user_id}/{date}  - 刪除路線")
    
    return success

if __name__ == "__main__":
    main()
