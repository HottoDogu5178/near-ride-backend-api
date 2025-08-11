# 用戶登錄API改進

## 概述
改進用戶登錄功能，提供更精確的錯誤訊息和更詳細的成功回應。

## API端點
```
POST /users/login
```

## 請求格式
```json
{
    "email": "user@example.com",
    "password": "userpassword"
}
```

## 回應格式

### 1. 登錄成功 (200)
```json
{
    "message": "登入成功",
    "user": {
        "id": "123",
        "email": "user@example.com",
        "nickname": "用戶暱稱",
        "avatar_url": "https://example.com/avatar.jpg",
        "gender": "男",
        "age": 25,
        "location": "台北市"
    },
    "login_time": "2025-08-11T14:30:00.123456"
}
```

### 2. 信箱未註冊 (404)
```json
{
    "detail": "此信箱尚未註冊"
}
```

### 3. 密碼錯誤 (401)
```json
{
    "detail": "密碼錯誤"
}
```

### 4. 系統錯誤 (500)
```json
{
    "detail": "系統錯誤"
}
```

## 功能特點

### 🔍 精確的錯誤識別
- **404錯誤**: 明確告知信箱未註冊，引導用戶去註冊
- **401錯誤**: 明確告知密碼錯誤，用戶可以重新輸入密碼
- **500錯誤**: 系統層級錯誤

### 📊 詳細的成功回應
- 基本用戶信息（ID、信箱）
- 個人資料（暱稱、頭像、性別、年齡、位置）
- 登錄時間戳記

### 🔐 安全考量
- 密碼驗證（目前使用明文比較，生產環境應使用加密）
- 登錄狀態更新（設置為在線狀態）
- 詳細的日誌記錄

### 📝 日誌記錄
- 登錄嘗試記錄
- 成功登錄記錄
- 失敗原因記錄（信箱不存在 vs 密碼錯誤）

## 測試

使用測試腳本驗證不同登錄情況：
```bash
python test_login_scenarios.py
```

測試包含：
1. 未註冊信箱登錄
2. 已註冊信箱但密碼錯誤
3. 正確信箱和密碼登錄

## 前端集成建議

### JavaScript 示例
```javascript
async function loginUser(email, password) {
    try {
        const response = await fetch('/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 登錄成功
            console.log('登錄成功:', data.user);
            localStorage.setItem('user', JSON.stringify(data.user));
            return { success: true, user: data.user };
        } else {
            // 登錄失敗
            if (response.status === 404) {
                return { success: false, error: '此信箱尚未註冊', needRegister: true };
            } else if (response.status === 401) {
                return { success: false, error: '密碼錯誤', needPassword: true };
            } else {
                return { success: false, error: data.detail || '登錄失敗' };
            }
        }
    } catch (error) {
        return { success: false, error: '網路錯誤' };
    }
}
```

## 改進歷史
- 原本統一回傳「帳號或密碼錯誤」
- 現在精確區分信箱不存在和密碼錯誤
- 增加詳細的用戶信息回應
- 添加登錄時間戳記
