#!/usr/bin/env python3
"""
測試用戶登錄的不同錯誤情況
"""

import requests
import json

def test_login_scenarios():
    """測試登錄的各種情況"""
    base_url = "http://localhost:8000"
    
    print("=== 測試用戶登錄功能 ===")
    
    # 測試數據
    test_cases = [
        {
            "name": "未註冊信箱",
            "data": {"email": "notregistered@example.com", "password": "anypassword"},
            "expected_status": 404,
            "expected_message": "此信箱尚未註冊"
        },
        {
            "name": "已註冊信箱但密碼錯誤",
            "data": {"email": "test@example.com", "password": "wrongpassword"},
            "expected_status": 401,
            "expected_message": "密碼錯誤"
        },
        {
            "name": "正確信箱和密碼",
            "data": {"email": "test@example.com", "password": "testpassword123"},
            "expected_status": 200,
            "expected_message": "登入成功"
        }
    ]
    
    try:
        # 首先確保有一個測試用戶存在
        print("0. 準備測試用戶...")
        register_data = {"email": "test@example.com", "password": "testpassword123"}
        register_response = requests.post(f"{base_url}/users/", json=register_data)
        if register_response.status_code == 200:
            print("   ✅ 測試用戶創建成功")
        elif register_response.status_code == 400 and "信箱重複" in register_response.text:
            print("   ✅ 測試用戶已存在")
        else:
            print(f"   ⚠️ 創建測試用戶回應: {register_response.status_code} - {register_response.text}")
        
        # 執行登錄測試
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 測試: {test_case['name']}")
            print(f"   信箱: {test_case['data']['email']}")
            print(f"   密碼: {test_case['data']['password']}")
            
            response = requests.post(f"{base_url}/users/login", json=test_case['data'])
            print(f"   狀態碼: {response.status_code}")
            
            # 檢查狀態碼
            if response.status_code == test_case['expected_status']:
                print(f"   ✅ 狀態碼正確 ({test_case['expected_status']})")
            else:
                print(f"   ❌ 狀態碼錯誤，期望: {test_case['expected_status']}, 實際: {response.status_code}")
            
            # 檢查回應內容
            try:
                response_data = response.json()
                if response.status_code == 200:
                    message = response_data.get("message", "")
                    if test_case['expected_message'] in message:
                        print(f"   ✅ 成功訊息正確: {message}")
                    else:
                        print(f"   ❌ 成功訊息錯誤: {message}")
                else:
                    detail = response_data.get("detail", "")
                    if test_case['expected_message'] in detail:
                        print(f"   ✅ 錯誤訊息正確: {detail}")
                    else:
                        print(f"   ❌ 錯誤訊息錯誤，期望包含: {test_case['expected_message']}, 實際: {detail}")
            except:
                print(f"   回應文本: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器，請確認服務器已啟動在 http://localhost:8000")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_login_scenarios()
