#!/usr/bin/env python3
"""
初始化興趣愛好數據的腳本
"""

if __name__ == "__main__":
    try:
        from app.database import initialize_hobbies
        print("正在初始化興趣愛好數據...")
        initialize_hobbies()
        print("興趣愛好數據初始化完成！")
    except Exception as e:
        print(f"初始化失敗: {e}")
        import traceback
        traceback.print_exc()
