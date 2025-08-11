#!/usr/bin/env python3
"""
測試興趣愛好數據庫操作
"""

if __name__ == "__main__":
    try:
        from app.database import SessionLocal
        from app.models.hobby import Hobby
        
        print("正在連接數據庫...")
        db = SessionLocal()
        
        # 檢查是否有興趣數據
        count = db.query(Hobby).count()
        print(f"當前興趣數量: {count}")
        
        if count > 0:
            print("前5個興趣:")
            hobbies = db.query(Hobby).limit(5).all()
            for hobby in hobbies:
                print(f"  {hobby.id}: {hobby.name} - {hobby.description}")
        
        db.close()
        print("數據庫連接測試完成！")
        
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()
