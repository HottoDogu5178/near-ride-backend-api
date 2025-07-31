import pytest
import requests
import json
from datetime import datetime

# 測試設定
BASE_URL = "http://localhost:8000"
TEST_USER_ID = 1

def test_record_gps_location():
    """測試記錄單個 GPS 定位點"""
    url = f"{BASE_URL}/gps/location"
    
    # 測試資料
    location_data = {
        "lat": 25.0330,  # 台北市的緯度
        "lng": 121.5654,  # 台北市的經度
        "ts": datetime.now().isoformat()
    }
    
    params = {"user_id": TEST_USER_ID}
    
    response = requests.post(url, json=location_data, params=params)
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["user_id"] == TEST_USER_ID
    assert data["latitude"] == location_data["lat"]
    assert data["longitude"] == location_data["lng"]
    
    return data["id"]

def test_get_user_locations():
    """測試獲取用戶的 GPS 定位歷史"""
    # 先記錄幾個定位點
    for i in range(3):
        test_record_gps_location()
    
    url = f"{BASE_URL}/gps/locations/{TEST_USER_ID}"
    
    response = requests.get(url)
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert data["user_id"] == TEST_USER_ID
    assert len(data["locations"]) >= 3

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
    
    response = requests.post(url, json=invalid_data, params=params)
    
    print(f"無效緯度測試 - 狀態碼: {response.status_code}")
    assert response.status_code == 422  # 驗證錯誤

def test_get_locations_by_date():
    """測試按日期獲取定位記錄"""
    # 記錄一個定位點
    test_record_gps_location()
    
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"{BASE_URL}/gps/locations/{TEST_USER_ID}/date/{today}"
    
    response = requests.get(url)
    
    print(f"按日期查詢 - 狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == today
    assert len(data["locations"]) >= 1

def test_delete_user_locations():
    """測試刪除用戶定位記錄"""
    # 先記錄一些定位點
    for i in range(2):
        test_record_gps_location()
    
    url = f"{BASE_URL}/gps/locations/{TEST_USER_ID}"
    
    response = requests.delete(url)
    
    print(f"刪除定位記錄 - 狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "deleted_count" in data
    assert data["deleted_count"] >= 2

if __name__ == "__main__":
    print("開始測試簡化的 GPS 系統...")
    
    try:
        print("\n1. 測試記錄 GPS 定位...")
        test_record_gps_location()
        
        print("\n2. 測試獲取定位歷史...")
        test_get_user_locations()
        
        print("\n3. 測試資料驗證...")
        test_gps_location_validation()
        
        print("\n4. 測試按日期查詢...")
        test_get_locations_by_date()
        
        print("\n5. 測試刪除定位記錄...")
        test_delete_user_locations()
        
        print("\n✅ 所有測試通過！")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
