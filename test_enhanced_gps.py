#!/usr/bin/env python3
"""
增強版 GPS 軌跡追蹤測試
測試完整的移動軌跡記錄功能
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_enhanced_gps_tracking():
    """測試增強版 GPS 軌跡追蹤功能"""
    print("🛣️ 測試增強版 GPS 軌跡追蹤...")
    
    user_id = "1"
    test_date = datetime.now().strftime("%Y-%m-%d")
    
    # 模擬一個完整的移動軌跡（從台北車站到台北 101）
    # 包含更多詳細資訊：海拔、精度、速度、方向
    enhanced_route_data = {
        "user_id": user_id,
        "date": test_date,
        "route": [
            {
                "lat": 25.047924,
                "lng": 121.517081,
                "ts": f"{test_date}T08:30:00.000Z",
                "altitude": 10.5,
                "accuracy": 5.0,
                "speed": 0.0,
                "heading": 0.0
            },
            {
                "lat": 25.047800,
                "lng": 121.517200,
                "ts": f"{test_date}T08:30:30.000Z",
                "altitude": 10.8,
                "accuracy": 4.5,
                "speed": 1.2,
                "heading": 45.0
            },
            {
                "lat": 25.047600,
                "lng": 121.517400,
                "ts": f"{test_date}T08:31:00.000Z",
                "altitude": 11.2,
                "accuracy": 4.0,
                "speed": 2.5,
                "heading": 90.0
            },
            {
                "lat": 25.047400,
                "lng": 121.517800,
                "ts": f"{test_date}T08:31:30.000Z",
                "altitude": 12.0,
                "accuracy": 3.8,
                "speed": 3.8,
                "heading": 120.0
            },
            {
                "lat": 25.047000,
                "lng": 121.518500,
                "ts": f"{test_date}T08:32:00.000Z",
                "altitude": 13.5,
                "accuracy": 4.2,
                "speed": 5.2,
                "heading": 135.0
            },
            {
                "lat": 25.046500,
                "lng": 121.519200,
                "ts": f"{test_date}T08:32:30.000Z",
                "altitude": 15.0,
                "accuracy": 3.5,
                "speed": 4.8,
                "heading": 150.0
            },
            {
                "lat": 25.045800,
                "lng": 121.520000,
                "ts": f"{test_date}T08:33:00.000Z",
                "altitude": 16.8,
                "accuracy": 3.2,
                "speed": 6.1,
                "heading": 180.0
            },
            {
                "lat": 25.044500,
                "lng": 121.521500,
                "ts": f"{test_date}T08:34:00.000Z",
                "altitude": 20.5,
                "accuracy": 2.8,
                "speed": 8.5,
                "heading": 210.0
            },
            {
                "lat": 25.042800,
                "lng": 121.524000,
                "ts": f"{test_date}T08:35:00.000Z",
                "altitude": 25.2,
                "accuracy": 2.5,
                "speed": 12.3,
                "heading": 225.0
            },
            {
                "lat": 25.040500,
                "lng": 121.528000,
                "ts": f"{test_date}T08:36:30.000Z",
                "altitude": 32.8,
                "accuracy": 2.2,
                "speed": 15.8,
                "heading": 240.0
            },
            {
                "lat": 25.037500,
                "lng": 121.535000,
                "ts": f"{test_date}T08:38:00.000Z",
                "altitude": 45.5,
                "accuracy": 1.8,
                "speed": 18.2,
                "heading": 270.0
            },
            {
                "lat": 25.034000,
                "lng": 121.545000,
                "ts": f"{test_date}T08:40:00.000Z",
                "altitude": 65.2,
                "accuracy": 1.5,
                "speed": 22.5,
                "heading": 285.0
            },
            {
                "lat": 25.033500,
                "lng": 121.564000,
                "ts": f"{test_date}T08:42:30.000Z",
                "altitude": 88.8,
                "accuracy": 1.2,
                "speed": 25.8,
                "heading": 300.0
            },
            {
                "lat": 25.033800,
                "lng": 121.564500,
                "ts": f"{test_date}T08:43:00.000Z",
                "altitude": 92.5,
                "accuracy": 1.0,
                "speed": 3.2,
                "heading": 315.0
            },
            {
                "lat": 25.034000,
                "lng": 121.564500,
                "ts": f"{test_date}T08:43:30.000Z",
                "altitude": 95.0,
                "accuracy": 0.8,
                "speed": 0.5,
                "heading": 0.0
            }
        ]
    }
    
    try:
        # 1. 上傳增強版 GPS 軌跡
        print("📤 上傳增強版 GPS 軌跡...")
        response = requests.post(f"{BASE_URL}/gps/upload", json=enhanced_route_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 軌跡上傳成功:")
            print(f"   點數: {result['point_count']}")
            print(f"   總距離: {result['total_distance']:.2f} 公尺")
            print(f"   開始時間: {result['start_time']}")
            print(f"   結束時間: {result['end_time']}")
        else:
            print(f"❌ 軌跡上傳失敗: {response.text}")
            return False
        
        # 2. 查詢路線統計資料
        print("\n📊 查詢路線統計資料...")
        response = requests.get(f"{BASE_URL}/gps/{user_id}/{test_date}")
        if response.status_code == 200:
            route_data = response.json()
            stats = route_data.get('statistics', {})
            print(f"✅ 路線統計:")
            print(f"   總點數: {stats.get('total_points', 0)}")
            print(f"   總距離: {stats.get('total_distance', 0):.2f} 公尺")
            print(f"   持續時間: {stats.get('duration_minutes', 0):.1f} 分鐘")
        else:
            print(f"❌ 統計查詢失敗: {response.text}")
        
        # 3. 查詢詳細 GPS 點資料
        print("\n🗺️ 查詢詳細 GPS 點資料...")
        response = requests.get(f"{BASE_URL}/gps/{user_id}/{test_date}/points")
        if response.status_code == 200:
            points_data = response.json()
            points = points_data.get('points', [])
            print(f"✅ 詳細點資料查詢成功:")
            print(f"   總點數: {len(points)}")
            
            # 顯示前 3 個點的詳細資料
            for i, point in enumerate(points[:3]):
                print(f"   點 {i+1}:")
                print(f"     位置: {point['latitude']:.6f}, {point['longitude']:.6f}")
                print(f"     時間: {point['timestamp']}")
                print(f"     海拔: {point['altitude']}m, 精度: {point['accuracy']}m")
                print(f"     速度: {point['speed']}m/s, 方向: {point['heading']}°")
        else:
            print(f"❌ 詳細點資料查詢失敗: {response.text}")
        
        # 4. 查詢軌跡歷史
        print("\n📋 查詢軌跡歷史...")
        response = requests.get(f"{BASE_URL}/gps/{user_id}/routes?limit=5")
        if response.status_code == 200:
            history = response.json()
            print(f"✅ 軌跡歷史查詢成功:")
            for route in history:
                print(f"   {route['date']}: {route['point_count']} 點, "
                      f"{route['total_distance']:.1f}m, "
                      f"{route['duration_minutes']:.1f} 分鐘")
        else:
            print(f"❌ 歷史查詢失敗: {response.text}")
        
        print("\n✅ 增強版 GPS 軌跡追蹤測試完成！")
        return True
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        return False

def main():
    """主程式"""
    print("🚀 開始增強版 GPS 軌跡追蹤測試...")
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
    
    success = test_enhanced_gps_tracking()
    
    if success:
        print("\n📋 增強版 GPS API 端點:")
        print("• POST /gps/upload                    - 上傳 GPS 軌跡（含詳細資訊）")
        print("• GET  /gps/{user_id}/{date}          - 獲取路線統計資料")
        print("• GET  /gps/{user_id}/{date}/points   - 獲取詳細 GPS 點資料")
        print("• GET  /gps/{user_id}/routes          - 獲取軌跡歷史（含統計）")
        print("• DELETE /gps/{user_id}/{date}        - 刪除路線")
        
        print("\n🆕 新增功能:")
        print("• 軌跡距離計算（Haversine 公式）")
        print("• 時間統計（開始/結束時間、持續時間）")
        print("• GPS 詳細資訊（海拔、精度、速度、方向）")
        print("• 軌跡分析和統計資料")

if __name__ == "__main__":
    main()
