# 用戶註冊錯誤處理改進

## 問題描述
用戶註冊時遇到重複信箱地址時，系統拋出數據庫級別的錯誤：
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "ix_users_email"
```

## 解決方案

### 1. 預防性檢查
在嘗試插入新用戶前，先檢查信箱是否已存在：
```python
existing_user = db.query(user.User).filter(user.User.email == user_data.email).first()
if existing_user:
    raise HTTPException(status_code=400, detail="信箱重複")
```

### 2. 異常處理
如果預防性檢查被繞過，添加 `IntegrityError` 異常處理：
```python
except IntegrityError as e:
    error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
    if "unique constraint" in error_str.lower() and "email" in error_str.lower():
        raise HTTPException(status_code=400, detail="信箱重複")
```

### 3. 錯誤回應格式
- **狀態碼**: 400 (Bad Request)
- **錯誤訊息**: "信箱重複"
- **日誌記錄**: 記錄重複註冊嘗試

## API 回應示例

### 成功註冊
```json
{
    "id": "123",
    "email": "user@example.com"
}
```

### 信箱重複錯誤
```json
{
    "detail": "信箱重複"
}
```

## 測試
使用 `test_duplicate_email.py` 腳本測試重複信箱處理：
```bash
python test_duplicate_email.py
```

## 改進後的流程
1. 接收註冊請求
2. 檢查信箱是否已存在
3. 如果存在，立即返回 400 錯誤
4. 如果不存在，創建新用戶
5. 如果數據庫層面仍有衝突，捕獲並處理 IntegrityError
6. 記錄相應的日誌信息
