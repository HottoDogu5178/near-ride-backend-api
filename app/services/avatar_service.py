"""
雲端頭像處理服務 - 適用於 Render 部署
"""

import base64
import os
import uuid
from datetime import datetime
from typing import Optional
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class CloudAvatarService:
    """雲端頭像處理服務"""
    
    def __init__(self):
        self.max_size = 1024
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_formats = ['JPEG', 'PNG', 'WEBP']
        
        # 檢查是否啟用雲端儲存
        self.use_cloud_storage = os.getenv('USE_CLOUD_STORAGE', 'false').lower() == 'true'
        self.cloudinary_url = os.getenv('CLOUDINARY_URL')
        
        # 診斷環境變數
        logger.info(f"USE_CLOUD_STORAGE: {os.getenv('USE_CLOUD_STORAGE')}")
        logger.info(f"CLOUDINARY_URL 是否設定: {'是' if self.cloudinary_url else '否'}")
        if self.cloudinary_url:
            # 只顯示 URL 的開頭部分，避免洩露敏感資訊
            logger.info(f"CLOUDINARY_URL 開頭: {self.cloudinary_url[:20]}...")
        
        # 初始化 Cloudinary
        if self.use_cloud_storage and self.cloudinary_url:
            try:
                # 驗證 URL 格式
                if not self.cloudinary_url.startswith('cloudinary://'):
                    raise ValueError(f"Invalid CLOUDINARY_URL scheme. Expecting to start with 'cloudinary://', got: {self.cloudinary_url[:20]}...")
                
                # 延遲匯入，避免安裝問題
                import cloudinary
                cloudinary.config(cloudinary_url=self.cloudinary_url)
                logger.info("Cloudinary 已初始化")
            except ImportError as e:
                logger.error(f"Cloudinary 套件未安裝: {e}")
                logger.warning("將使用本地儲存作為備用方案")
                self.use_cloud_storage = False
            except Exception as e:
                logger.error(f"Cloudinary 初始化失敗: {e}")
                logger.warning("將使用本地儲存作為備用方案")
                self.use_cloud_storage = False
        else:
            if self.use_cloud_storage and not self.cloudinary_url:
                logger.error("啟用了雲端儲存但未設定 CLOUDINARY_URL")
            logger.warning("未啟用雲端儲存，將使用本地儲存（不適用於生產環境）")
    
    def validate_base64_image(self, base64_data: str) -> Image.Image:
        """驗證 base64 圖片資料"""
        try:
            # 移除 data URL 前綴
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            # 解碼 base64
            image_data = base64.b64decode(base64_data)
            
            # 檢查檔案大小
            if len(image_data) > self.max_file_size:
                raise ValueError(f"圖片檔案過大：{len(image_data)} bytes")
            
            # 開啟圖片
            image = Image.open(BytesIO(image_data))
            
            # 檢查格式
            if image.format not in self.allowed_formats:
                raise ValueError(f"不支援的格式：{image.format}")
            
            return image
            
        except Exception as e:
            raise ValueError(f"圖片資料無效: {str(e)}")
    
    def process_avatar_image(self, image: Image.Image) -> BytesIO:
        """處理頭像圖片並返回位元組流"""
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
        
        # 轉換為位元組流
        output = BytesIO()
        image.save(output, format='WEBP', quality=85, optimize=True)
        output.seek(0)
        return output
    
    def upload_to_cloudinary(self, image_bytes: BytesIO, user_id: int) -> str:
        """上傳到 Cloudinary"""
        try:
            import cloudinary
            from cloudinary import uploader
            
            # 生成唯一的 public_id
            public_id = f"avatars/user_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # 上傳到 Cloudinary
            result = uploader.upload(
                image_bytes,
                public_id=public_id,
                resource_type="image",
                format="webp",
                quality="85",
                fetch_format="auto",
                width=1024,
                height=1024,
                crop="limit",
                overwrite=True,  # 允許覆蓋相同 public_id 的圖片
                invalidate=True  # 清除 CDN 快取
            )
            
            logger.info(f"圖片已上傳到 Cloudinary: {result['public_id']}")
            return result['secure_url']
            
        except Exception as e:
            logger.error(f"Cloudinary 上傳失敗: {e}")
            raise ValueError(f"雲端上傳失敗: {str(e)}")
    
    def save_avatar_fallback(self, image_bytes: BytesIO, user_id: int) -> str:
        """本地儲存備用方案（僅開發環境）"""
        try:
            # 在 Render 上使用 /tmp 目錄
            upload_dir = "/tmp/avatars" if os.path.exists("/tmp") else "uploads/avatars"
            os.makedirs(upload_dir, exist_ok=True)
            
            filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.webp"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes.read())
            
            # 本地 URL（注意：在 Render 上重啟後會遺失）
            return f"http://localhost:8001/static/avatars/{filename}"
            
        except Exception as e:
            logger.error(f"本地儲存失敗: {e}")
            raise ValueError(f"儲存失敗: {str(e)}")
    
    def save_avatar(self, avatar_base64: str, user_id: int, request_url: Optional[str] = None) -> str:
        """儲存頭像（自動選擇雲端或本地）"""
        try:
            # 驗證和處理圖片
            image = self.validate_base64_image(avatar_base64)
            image_bytes = self.process_avatar_image(image)
            
            # 選擇儲存方式
            if self.use_cloud_storage and self.cloudinary_url:
                return self.upload_to_cloudinary(image_bytes, user_id)
            else:
                logger.warning("使用本地儲存 - 在生產環境中圖片會在重啟後遺失")
                return self.save_avatar_fallback(image_bytes, user_id)
                
        except Exception as e:
            logger.error(f"頭像儲存失敗: {e}")
            raise ValueError(f"頭像處理失敗: {str(e)}")
    
    def delete_avatar(self, avatar_url: str) -> bool:
        """刪除頭像"""
        try:
            if self.use_cloud_storage and 'cloudinary' in avatar_url:
                return self._delete_from_cloudinary(avatar_url)
            else:
                return self._delete_local_avatar(avatar_url)
                
        except Exception as e:
            logger.error(f"刪除頭像失敗: {e}")
            return False
    
    def _delete_from_cloudinary(self, avatar_url: str) -> bool:
        """從 Cloudinary 刪除"""
        try:
            import cloudinary
            from cloudinary import uploader
            
            # 從 URL 提取 public_id
            # URL 格式: https://res.cloudinary.com/cloud-name/image/upload/v123456/avatars/user_1_abc123.webp
            url_parts = avatar_url.split('/')
            if 'avatars' in url_parts:
                avatar_index = url_parts.index('avatars')
                filename = url_parts[avatar_index + 1].split('.')[0]  # 移除副檔名
                public_id = f"avatars/{filename}"
                
                result = uploader.destroy(public_id)
                logger.info(f"Cloudinary 刪除結果: {result}")
                return result.get('result') == 'ok'
            
            return False
            
        except Exception as e:
            logger.error(f"Cloudinary 刪除失敗: {e}")
            return False
    
    def _delete_local_avatar(self, avatar_url: str) -> bool:
        """刪除本地檔案"""
        try:
            filename = avatar_url.split('/')[-1]
            upload_dir = "/tmp/avatars" if os.path.exists("/tmp") else "uploads/avatars"
            filepath = os.path.join(upload_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
            
        except Exception as e:
            logger.error(f"本地刪除失敗: {e}")
            return False

# 雲端頭像服務實例
cloud_avatar_service = CloudAvatarService()
