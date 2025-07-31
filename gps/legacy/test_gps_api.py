#!/usr/bin/env python3
"""
測試 GPS 定位功能的腳本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_gps_functionality():
    """測試 GPS 定位相關功能"""
    print("🌍 測試 GPS 定位功能...")
    
    user_id = 1  # 測試用戶 ID
    
    # 測試用的 GPS 座標（台北 101 附近）
    test_location = {
        "latitude": 25.0340,
        "longitude": 121.5645
    }
    
    try:
        # 1. 更新用戶定位
        print("\n📍 測試更新用戶定位...")
        response = requests.post(f"{BASE_URL}/users/{user_id}/location", json=test_location)
        if response.status_code == 200:
            location_data = response.json()
            print(f"✅ 定位更新成功: {json.dumps(location_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 定位更新失敗: {response.text}")
            return
        
        # 2. 獲取用戶定位
        print("\n📍 測試獲取用戶定位...")
        response = requests.get(f"{BASE_URL}/users/{user_id}/location")
        if response.status_code == 200:
            location_data = response.json()
            print(f"✅ 獲取定位成功: {json.dumps(location_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 獲取定位失敗: {response.text}")
        
        # 3. 獲取用戶完整資料（包含定位）
        print("\n👤 測試獲取用戶完整資料...")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 用戶資料（含定位）: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 獲取用戶資料失敗: {response.text}")
        
        # 4. 測試附近用戶查詢
        print("\n🔍 測試查詢附近用戶...")
        response = requests.get(f"{BASE_URL}/users/{user_id}/nearby?radius_km=10")
        if response.status_code == 200:
            nearby_users = response.json()
            print(f"✅ 找到 {len(nearby_users)} 個附近用戶")
            for nearby_user in nearby_users[:3]:  # 只顯示前 3 個
                print(f"   - {nearby_user.get('nickname', 'Unknown')} (ID: {nearby_user['id']})")
        else:
            print(f"❌ 查詢附近用戶失敗: {response.text}")
        
        # 5. 測試通過 PATCH 更新定位
        print("\n📍 測試通過 PATCH 更新定位...")
        update_data = {
            "latitude": 25.0470,  # 稍微移動位置
            "longitude": 121.5174
        }
        response = requests.patch(f"{BASE_URL}/users/{user_id}", json=update_data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ PATCH 更新定位成功: lat={user_data.get('latitude')}, lng={user_data.get('longitude')}")
        else:
            print(f"❌ PATCH 更新定位失敗: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確認伺服器已啟動")
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")

def test_invalid_coordinates():
    """測試無效座標的處理"""
    print("\n⚠️  測試無效座標處理...")
    
    invalid_coordinates = [
        {"latitude": 91.0, "longitude": 121.0},    # 緯度超出範圍
        {"latitude": 25.0, "longitude": 181.0},    # 經度超出範圍
        {"latitude": -91.0, "longitude": -181.0},  # 都超出範圍
    ]
    
    for i, coords in enumerate(invalid_coordinates, 1):
        try:
            response = requests.post(f"{BASE_URL}/users/1/location", json=coords)
            if response.status_code == 400:
                print(f"✅ 測試 {i}: 正確拒絕無效座標 {coords}")
            else:
                print(f"❌ 測試 {i}: 應該拒絕無效座標但沒有 {coords}")
        except Exception as e:
            print(f"❌ 測試 {i} 發生錯誤: {e}")

def main():
    print("🚀 開始 GPS 定位功能測試...")
    print(f"目標伺服器: {BASE_URL}")
    
    # 測試基本連接
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ 伺服器連接正常")
        else:
            print("❌ 伺服器連接異常")
            return
    except:
        print("❌ 無法連接到伺服器")
        return
    
    test_gps_functionality()
    test_invalid_coordinates()
    
    print("\n🎉 GPS 功能測試完成！")

if __name__ == "__main__":
    main()
