"""
GPS 定位系統測試檔

此檔案包含簡化 GPS 系統的所有測試用例，包括：
- GPS 定位記錄
- 定位歷史查詢  
- 資料驗證
- 按日期篩選
- 刪除操作

使用方式：
    python test_simple_gps.py

或使用 pytest：
    pytest test_simple_gps.py -v
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# 將父目錄加入 Python 路徑以便導入模組
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 測試設定
BASE_URL = "http://localhost:8001"  # 更新為正確的端口
TEST_USER_ID = 1

class TestGPSSystem:
    """GPS 系統測試類別"""
    
    @staticmethod
    def test_server_connection():
        """測試服務器連接"""
        try:
            response = requests.get(f"{BASE_URL}/docs")
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def test_record_gps_location():
        """測試記錄單個 GPS 定位點"""
        url = f"{BASE_URL}/gps/location"
        
        # 測試資料 - 台北市中心位置
        location_data = {
            "lat": 25.0330,
            "lng": 121.5654,
            "ts": datetime.now().isoformat()
        }
        
        params = {"user_id": TEST_USER_ID}
        
        try:
            response = requests.post(url, json=location_data, params=params)
            
            print(f"✓ 記錄 GPS 定位 - 狀態碼: {response.status_code}")
            
            assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
            
            data = response.json()
            assert "id" in data, "回應中缺少 id 欄位"
            assert data["user_id"] == TEST_USER_ID, f"用戶 ID 不符，期望 {TEST_USER_ID}，實際 {data['user_id']}"
            assert data["latitude"] == location_data["lat"], f"緯度不符"
            assert data["longitude"] == location_data["lng"], f"經度不符"
            
            print(f"  成功記錄定位點 ID: {data['id']}")
            return data["id"]
            
        except requests.exceptions.ConnectionError:
            print("❌ 無法連接到服務器，請確認服務器已啟動")
            return None
        except Exception as e:
            print(f"❌ 記錄 GPS 定位失敗: {e}")
            return None

    @staticmethod
    def test_get_user_locations():
        """測試獲取用戶的 GPS 定位歷史"""
        # 先記錄幾個定位點
        location_ids = []
        for i in range(3):
            location_id = TestGPSSystem.test_record_gps_location()
            if location_id:
                location_ids.append(location_id)
        
        url = f"{BASE_URL}/gps/locations/{TEST_USER_ID}"
        
        try:
            response = requests.get(url)
            
            print(f"✓ 獲取定位歷史 - 狀態碼: {response.status_code}")
            
            assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
            
            data = response.json()
            assert "locations" in data, "回應中缺少 locations 欄位"
            assert data["user_id"] == TEST_USER_ID, f"用戶 ID 不符"
            assert len(data["locations"]) >= len(location_ids), f"定位記錄數量不符"
            
            print(f"  用戶 {TEST_USER_ID} 共有 {data['total_locations']} 個定位記錄")
            return True
            
        except Exception as e:
            print(f"❌ 獲取定位歷史失敗: {e}")
            return False

    @staticmethod
    def test_gps_location_validation():
        """測試 GPS 定位資料驗證"""
        url = f"{BASE_URL}/gps/location"
        
        # 測試無效的緯度
        invalid_data = {
            "lat": 91.0,  # 超出範圍
            "lng": 121.5654,
            "ts": datetime.now().isoformat()
        }
        
        params = {"user_id": TEST_USER_ID}
        
        try:
            response = requests.post(url, json=invalid_data, params=params)
            
            print(f"✓ 資料驗證測試 - 狀態碼: {response.status_code}")
            
            assert response.status_code == 422, f"期望驗證錯誤狀態碼 422，實際 {response.status_code}"
            
            print("  無效緯度正確被拒絕")
            return True
            
        except Exception as e:
            print(f"❌ 資料驗證測試失敗: {e}")
            return False

    @staticmethod
    def test_get_locations_by_date():
        """測試按日期獲取定位記錄"""
        # 記錄一個定位點
        location_id = TestGPSSystem.test_record_gps_location()
        if not location_id:
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"{BASE_URL}/gps/locations/{TEST_USER_ID}/date/{today}"
        
        try:
            response = requests.get(url)
            
            print(f"✓ 按日期查詢 - 狀態碼: {response.status_code}")
            
            assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
            
            data = response.json()
            assert data["date"] == today, f"日期不符"
            assert len(data["locations"]) >= 1, f"應至少有一個定位記錄"
            
            print(f"  {today} 共有 {data['total_locations']} 個定位記錄")
            return True
            
        except Exception as e:
            print(f"❌ 按日期查詢失敗: {e}")
            return False

    @staticmethod
    def test_batch_location_recording():
        """測試批量記錄 GPS 定位點"""
        print("✓ 開始批量記錄測試...")
        
        # 模擬一條移動路徑（從台北車站到台北101）
        locations = [
            {"lat": 25.0478, "lng": 121.5170, "name": "台北車站"},
            {"lat": 25.0485, "lng": 121.5180, "name": "移動中1"},
            {"lat": 25.0495, "lng": 121.5190, "name": "移動中2"},
            {"lat": 25.0336, "lng": 121.5650, "name": "台北101"}
        ]
        
        successful_records = 0
        for i, loc in enumerate(locations):
            location_data = {
                "lat": loc["lat"],
                "lng": loc["lng"],
                "ts": (datetime.now() + timedelta(minutes=i)).isoformat()
            }
            
            params = {"user_id": TEST_USER_ID}
            
            try:
                response = requests.post(f"{BASE_URL}/gps/location", json=location_data, params=params)
                if response.status_code == 200:
                    successful_records += 1
                    print(f"  記錄 {loc['name']}: ✓")
                else:
                    print(f"  記錄 {loc['name']}: ❌ ({response.status_code})")
            except Exception as e:
                print(f"  記錄 {loc['name']}: ❌ ({e})")
        
        print(f"  成功記錄 {successful_records}/{len(locations)} 個位置")
        return successful_records == len(locations)

    @staticmethod 
    def test_delete_user_locations():
        """測試刪除用戶定位記錄"""
        # 先記錄一些定位點
        print("✓ 準備刪除測試資料...")
        for i in range(2):
            TestGPSSystem.test_record_gps_location()
        
        url = f"{BASE_URL}/gps/locations/{TEST_USER_ID}"
        
        try:
            response = requests.delete(url)
            
            print(f"✓ 刪除定位記錄 - 狀態碼: {response.status_code}")
            
            assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
            
            data = response.json()
            assert "deleted_count" in data, "回應中缺少 deleted_count 欄位"
            assert data["deleted_count"] >= 2, f"刪除數量不符，期望至少 2，實際 {data['deleted_count']}"
            
            print(f"  成功刪除 {data['deleted_count']} 個定位記錄")
            return True
            
        except Exception as e:
            print(f"❌ 刪除定位記錄失敗: {e}")
            return False


def run_all_tests():
    """執行所有測試"""
    print("=" * 60)
    print("GPS 定位系統測試開始")
    print("=" * 60)
    
    # 檢查服務器連接
    if not TestGPSSystem.test_server_connection():
        print("❌ 無法連接到服務器，請確認服務器已在 http://localhost:8001 啟動")
        return False
    
    print("✓ 服務器連接正常")
    print()
    
    # 執行所有測試
    tests = [
        ("記錄 GPS 定位點", TestGPSSystem.test_record_gps_location),
        ("獲取定位歷史", TestGPSSystem.test_get_user_locations),
        ("資料驗證", TestGPSSystem.test_gps_location_validation),
        ("按日期查詢", TestGPSSystem.test_get_locations_by_date),
        ("批量記錄", TestGPSSystem.test_batch_location_recording),
        ("刪除記錄", TestGPSSystem.test_delete_user_locations)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📍 測試: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} - 通過")
                passed += 1
            else:
                print(f"❌ {test_name} - 失敗")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} - 錯誤: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    print(f"✅ 通過: {passed}")
    print(f"❌ 失敗: {failed}")
    print(f"📊 總計: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有測試都通過了！GPS 系統運作正常。")
        return True
    else:
        print(f"\n⚠️  有 {failed} 個測試失敗，請檢查系統配置。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
