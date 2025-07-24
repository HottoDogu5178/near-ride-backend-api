#!/usr/bin/env python3
"""
測試 API 功能的腳本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_operations():
    """測試用戶相關操作"""
    print("🧪 測試用戶 API...")
    
    # 測試建立用戶資料（假設用戶 ID 1 存在）
    user_data = {
        "nickname": "測試用戶",
        "gender": "male", 
        "age": 25,
        "location": "台北市",
        "hobby_ids": []
    }
    
    try:
        # 測試更新用戶資料
        response = requests.patch(f"{BASE_URL}/users/1", json=user_data)
        print(f"更新用戶資料: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 用戶資料更新成功")
        else:
            print(f"❌ 用戶資料更新失敗: {response.text}")
            
        # 測試獲取用戶資料
        response = requests.get(f"{BASE_URL}/users/1")
        print(f"獲取用戶資料: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 用戶資料: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 獲取用戶資料失敗: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確認伺服器已啟動")
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")

def test_hobby_operations():
    """測試興趣愛好相關操作"""
    print("\n🎯 測試興趣愛好...")
    
    try:
        # 測試獲取所有興趣
        response = requests.get(f"{BASE_URL}/hobbies")
        print(f"獲取興趣列表: {response.status_code}")
        if response.status_code == 200:
            hobbies = response.json()
            print(f"✅ 興趣列表: {json.dumps(hobbies, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 獲取興趣列表失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試興趣操作時發生錯誤: {e}")

def main():
    print("🚀 開始 API 測試...")
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
    
    test_user_operations()
    test_hobby_operations()
    
    print("\n🎉 API 測試完成！")

if __name__ == "__main__":
    main()
