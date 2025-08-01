"""
簡化版頭像服務 - 使用 imgur 作為替代方案
適用於 Render 部署的備用選項
"""

import base64
import os
import uuid
import requests
from io import BytesIO
from PIL import Image
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ImgurAvatarService:
    """使用 Imgur 的頭像服務"""
    
    def __init__(self):
        self.max_size = 1024
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_formats = ['JPEG', 'PNG', 'WEBP']
        
        # Imgur 設定
        self.imgur_client_id = os.getenv('IMGUR_CLIENT_ID')
        self.use_imgur = bool(self.imgur_client_id)
        
        if self.use_imgur:
            logger.info("使用 Imgur 雲端儲存")
        else:
            logger.warning("未設定 Imgur，將使用本地儲存")
    
    def validate_base64_image(self, base64_data: str) -> Image.Image:
        """驗證 base64 圖片資料"""
        try:
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            image_data = base64.b64decode(base64_data)
            
            if len(image_data) > self.max_file_size:
                raise ValueError(f"圖片檔案過大：{len(image_data)} bytes")
            
            image = Image.open(BytesIO(image_data))
            
            if image.format not in self.allowed_formats:
                raise ValueError(f"不支援的格式：{image.format}")
            
            return image
            
        except Exception as e:
            raise ValueError(f"圖片資料無效: {str(e)}")
    
    def process_avatar_image(self, image: Image.Image) -> BytesIO:
        """處理頭像圖片"""
        # 轉換為 RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 調整大小
        width, height = image.size
        if width > self.max_size or height > self.max_size:
            if width > height:
                new_width = self.max_size
                new_height = int((height * self.max_size) / width)
            else:
                new_height = self.max_size
                new_width = int((width * self.max_size) / height)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 輸出
        output = BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        return output
    
    def upload_to_imgur(self, image_bytes: BytesIO, user_id: int) -> str:
        """上傳到 Imgur"""
        try:
            # Imgur API
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": f"Client-ID {self.imgur_client_id}"}
            
            # 轉換為 base64
            image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
            
            data = {
                'image': image_base64,
                'type': 'base64',
                'title': f'Avatar for user {user_id}',
                'description': f'Near Ride user avatar'
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                image_url = result['data']['link']
                logger.info(f"圖片已上傳到 Imgur: {image_url}")
                return image_url
            else:
                raise Exception(f"Imgur 上傳失敗: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Imgur 上傳失敗: {e}")
            raise ValueError(f"雲端上傳失敗: {str(e)}")
    
    def save_avatar_fallback(self, image_bytes: BytesIO, user_id: int) -> str:
        """本地儲存"""
        try:
            upload_dir = "/tmp/avatars" if os.path.exists("/tmp") else "uploads/avatars"
            os.makedirs(upload_dir, exist_ok=True)
            
            filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes.read())
            
            return f"/static/avatars/{filename}"
            
        except Exception as e:
            logger.error(f"本地儲存失敗: {e}")
            raise ValueError(f"儲存失敗: {str(e)}")
    
    def save_avatar(self, avatar_base64: str, user_id: int, request_url: Optional[str] = None) -> str:
        """儲存頭像"""
        try:
            image = self.validate_base64_image(avatar_base64)
            image_bytes = self.process_avatar_image(image)
            
            if self.use_imgur:
                return self.upload_to_imgur(image_bytes, user_id)
            else:
                local_path = self.save_avatar_fallback(image_bytes, user_id)
                # 構建完整 URL
                if request_url:
                    from urllib.parse import urlparse
                    parsed = urlparse(request_url)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    return f"{base_url}{local_path}"
                return f"http://localhost:8001{local_path}"
                
        except Exception as e:
            logger.error(f"頭像儲存失敗: {e}")
            raise ValueError(f"頭像處理失敗: {str(e)}")
    
    def delete_avatar(self, avatar_url: str) -> bool:
        """刪除頭像"""
        try:
            if 'imgur.com' in avatar_url:
                # Imgur 不支援透過 Client ID 刪除，需要 Access Token
                logger.warning("Imgur 圖片無法透過 Client ID 刪除")
                return True  # 假設成功，避免錯誤
            else:
                # 本地檔案
                filename = avatar_url.split('/')[-1]
                upload_dir = "/tmp/avatars" if os.path.exists("/tmp") else "uploads/avatars"
                filepath = os.path.join(upload_dir, filename)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return True
                return False
                
        except Exception as e:
            logger.error(f"刪除頭像失敗: {e}")
            return False

# 簡化版頭像服務實例
simple_avatar_service = ImgurAvatarService()
