#!/usr/bin/env python3
"""
測試用戶註冊的重複信箱處理
"""

import requests
import json

def test_duplicate_email():
    """測試重複信箱註冊"""
    base_url = "http://localhost:8000"
    
    # 測試用戶數據
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print("=== 測試重複信箱註冊 ===")
    
    try:
        # 第一次註冊（應該成功）
        print("1. 第一次註冊...")
        response1 = requests.post(f"{base_url}/users/", json=test_user)
        print(f"   狀態碼: {response1.status_code}")
        if response1.status_code == 200:
            print(f"   回應: {response1.json()}")
            print("   ✅ 第一次註冊成功")
        else:
            print(f"   回應: {response1.text}")
            print("   ❌ 第一次註冊失敗")
            return
        
        # 第二次註冊（應該失敗並返回信箱重複）
        print("\n2. 重複信箱註冊...")
        response2 = requests.post(f"{base_url}/users/", json=test_user)
        print(f"   狀態碼: {response2.status_code}")
        
        if response2.status_code == 400:
            try:
                error_detail = response2.json().get("detail", "")
                print(f"   錯誤訊息: {error_detail}")
                if "信箱重複" in error_detail:
                    print("   ✅ 正確回傳信箱重複錯誤")
                else:
                    print("   ❌ 錯誤訊息不正確")
            except:
                print(f"   回應文本: {response2.text}")
        else:
            print(f"   回應: {response2.text}")
            print("   ❌ 重複註冊沒有正確處理")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器，請確認服務器已啟動在 http://localhost:8000")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_duplicate_email()
