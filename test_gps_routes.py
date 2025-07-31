#!/usr/bin/env python3
"""
測試 GPS 路線追蹤功能的腳本
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_gps_route_functionality():
    """測試 GPS 路線追蹤相關功能"""
    print("🛣️ 測試 GPS 路線追蹤功能...")
    
    user_id = "1"
    test_date = "2025-01-31"
    
    # 測試用的 GPS 路線資料（模擬從台北車站到台北 101 的路線）
    test_route_data = {
        "user_id": user_id,
        "date": test_date,
        "route": [
            {
                "lat": 25.0478,
                "lng": 121.5173,
                "ts": "2025-01-31T08:30:00.000Z"
            },
            {
                "lat": 25.0465,
                "lng": 121.5168,
                "ts": "2025-01-31T08:32:00.000Z"
            },
            {
                "lat": 25.0452,
                "lng": 121.5162,
                "ts": "2025-01-31T08:34:00.000Z"
            },
            {
                "lat": 25.0441,
                "lng": 121.5155,
                "ts": "2025-01-31T08:36:00.000Z"
            },
            {
                "lat": 25.0340,
                "lng": 121.5645,
                "ts": "2025-01-31T08:45:00.000Z"
            }
        ]
    }
    
    try:
        # 1. 上傳 GPS 路線資料
        print("\n📤 測試上傳 GPS 路線資料...")
        response = requests.post(f"{BASE_URL}/gps/upload", json=test_route_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GPS 路線上傳成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ GPS 路線上傳失敗: {response.text}")
            return
        
        # 2. 獲取指定日期的 GPS 路線
        print(f"\n📥 測試獲取 {test_date} 的 GPS 路線...")
        response = requests.get(f"{BASE_URL}/gps/{user_id}/{test_date}")
        if response.status_code == 200:
            route_data = response.json()
            print(f"✅ 獲取 GPS 路線成功:")
            print(f"   用戶 ID: {route_data['user_id']}")
            print(f"   日期: {route_data['date']}")
            print(f"   路線點數: {len(route_data['route'])}")
            # 只顯示前 2 個點
            for i, point in enumerate(route_data['route'][:2]):
                print(f"   點 {i+1}: lat={point['lat']}, lng={point['lng']}, time={point['ts']}")
        else:
            print(f"❌ 獲取 GPS 路線失敗: {response.text}")
        
        # 3. 獲取用戶的 GPS 路線歷史
        print(f"\n📋 測試獲取用戶 {user_id} 的路線歷史...")
        response = requests.get(f"{BASE_URL}/gps/{user_id}/routes?limit=10")
        if response.status_code == 200:
            routes_history = response.json()
            print(f"✅ 找到 {len(routes_history)} 條路線記錄:")
            for route in routes_history:
                print(f"   - {route['date']}: {route['point_count']} 個點")
        else:
            print(f"❌ 獲取路線歷史失敗: {response.text}")
        
        # 4. 測試更新現有路線（相同日期，新資料）
        print(f"\n🔄 測試更新現有路線...")
        updated_route_data = {
            "user_id": user_id,
            "date": test_date,
            "route": [
                {
                    "lat": 25.0478,
                    "lng": 121.5173,
                    "ts": "2025-01-31T09:00:00.000Z"
                },
                {
                    "lat": 25.0340,
                    "lng": 121.5645,
                    "ts": "2025-01-31T09:15:00.000Z"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/gps/upload", json=updated_route_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 路線更新成功: 點數從 5 個更新為 {result['point_count']} 個")
        else:
            print(f"❌ 路線更新失敗: {response.text}")
        
        # 5. 測試刪除路線
        print(f"\n🗑️ 測試刪除路線...")
        response = requests.delete(f"{BASE_URL}/gps/{user_id}/{test_date}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 路線刪除成功: {result['message']}")
        else:
            print(f"❌ 路線刪除失敗: {response.text}")
        
        # 6. 確認刪除後無法獲取
        print(f"\n🔍 確認刪除後無法獲取路線...")
        response = requests.get(f"{BASE_URL}/gps/{user_id}/{test_date}")
        if response.status_code == 404:
            print("✅ 確認路線已被刪除")
        else:
            print(f"❌ 預期應該找不到路線，但回應為: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確認伺服器已啟動")
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")

def test_invalid_gps_data():
    """測試無效 GPS 資料的處理"""
    print("\n⚠️  測試無效 GPS 資料處理...")
    
    invalid_data_sets = [
        {
            "name": "空路線",
            "data": {
                "user_id": "1",
                "date": "2025-01-31",
                "route": []
            }
        },
        {
            "name": "無效緯度",
            "data": {
                "user_id": "1",
                "date": "2025-01-31",
                "route": [
                    {
                        "lat": 91.0,  # 超出範圍
                        "lng": 121.5173,
                        "ts": "2025-01-31T08:30:00.000Z"
                    }
                ]
            }
        },
        {
            "name": "無效經度",
            "data": {
                "user_id": "1",
                "date": "2025-01-31",
                "route": [
                    {
                        "lat": 25.0478,
                        "lng": 181.0,  # 超出範圍
                        "ts": "2025-01-31T08:30:00.000Z"
                    }
                ]
            }
        },
        {
            "name": "不存在的用戶",
            "data": {
                "user_id": "99999",
                "date": "2025-01-31",
                "route": [
                    {
                        "lat": 25.0478,
                        "lng": 121.5173,
                        "ts": "2025-01-31T08:30:00.000Z"
                    }
                ]
            }
        }
    ]
    
    for test_case in invalid_data_sets:
        try:
            response = requests.post(f"{BASE_URL}/gps/upload", json=test_case["data"])
            if response.status_code == 400 or response.status_code == 404:
                print(f"✅ {test_case['name']}: 正確拒絕無效資料")
            else:
                print(f"❌ {test_case['name']}: 應該拒絕但沒有，狀態碼: {response.status_code}")
        except Exception as e:
            print(f"❌ {test_case['name']} 測試發生錯誤: {e}")

def main():
    print("🚀 開始 GPS 路線追蹤功能測試...")
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
    
    test_gps_route_functionality()
    test_invalid_gps_data()
    
    print("\n🎉 GPS 路線追蹤功能測試完成！")
    print("\n📋 API 端點總覽:")
    print("• POST /gps/upload          - 上傳 GPS 路線資料")
    print("• GET  /gps/{user_id}/{date} - 獲取指定日期路線")
    print("• GET  /gps/{user_id}/routes - 獲取路線歷史")
    print("• DELETE /gps/{user_id}/{date} - 刪除指定路線")

if __name__ == "__main__":
    main()
