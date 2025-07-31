"""
頭像處理服務

提供頭像圖片的上傳、處理和 URL 生成功能
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

class AvatarService:
    """頭像處理服務類別"""
    
    def __init__(self, upload_dir: str = "uploads/avatars", base_url: Optional[str] = None):
        """
        初始化頭像服務
        
        Args:
            upload_dir: 頭像上傳目錄
            base_url: 基礎 URL，如果為 None 則使用請求的主機
        """
        self.upload_dir = upload_dir
        self.base_url = base_url  # 將在運行時設定
        self.max_size = 1024  # 最大尺寸 1024x1024
        self.max_file_size = 5 * 1024 * 1024  # 最大檔案大小 5MB
        self.allowed_formats = ['JPEG', 'PNG', 'WEBP']
        
        # 確保上傳目錄存在
        os.makedirs(upload_dir, exist_ok=True)
    
    def validate_base64_image(self, base64_data: str) -> Image.Image:
        """
        驗證 base64 格式的圖片並返回 Image 對象
        
        Args:
            base64_data: base64 編碼的圖片資料
            
        Returns:
            Image.Image: PIL Image 對象
            
        Raises:
            ValueError: 當圖片資料無效時
        """
        try:
            # 移除 data URL 前綴（如果存在）
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            # 解碼 base64
            image_data = base64.b64decode(base64_data)
            
            # 檢查檔案大小
            if len(image_data) > self.max_file_size:
                raise ValueError(f"圖片檔案過大：{len(image_data)} 位元組，最大允許：{self.max_file_size} 位元組")
            
            # 嘗試開啟圖片
            image = Image.open(BytesIO(image_data))
            
            # 檢查圖片格式
            if image.format not in self.allowed_formats:
                raise ValueError(f"不支援的圖片格式：{image.format}，支援格式：{', '.join(self.allowed_formats)}")
            
            return image
            
        except Exception as e:
            logger.error(f"Base64 圖片驗證失敗: {e}")
            raise ValueError(f"圖片資料無效: {str(e)}")
    
    def process_avatar_image(self, image: Image.Image) -> Image.Image:
        """
        處理頭像圖片（調整大小、格式等）
        
        Args:
            image: PIL Image 物件
            
        Returns:
            Image.Image: 處理後的圖片
        """
        # 轉換為 RGB 模式（確保 JPEG 相容性）
        if image.mode in ('RGBA', 'LA', 'P'):
            # 建立白色背景
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 調整圖片大小，保持比例
        width, height = image.size
        if width > self.max_size or height > self.max_size:
            # 計算新尺寸，保持長寬比
            if width > height:
                new_width = self.max_size
                new_height = int((height * self.max_size) / width)
            else:
                new_height = self.max_size
                new_width = int((width * self.max_size) / height)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def save_avatar(self, avatar_base64: str, user_id: int, request_url: Optional[str] = None) -> str:
        """
        儲存 base64 格式的頭像圖片
        
        Args:
            avatar_base64: base64 編碼的圖片資料
            user_id: 用戶 ID
            request_url: 請求的 URL，用於構建頭像 URL
            
        Returns:
            頭像的公開 URL
            
        Raises:
            ValueError: 當圖片資料無效時
        """
        try:
            # 驗證 base64 格式
            image_data = self.validate_base64_image(avatar_base64)
            
            # 處理圖片
            processed_image = self.process_avatar_image(image_data)
            
            # 生成檔案名稱
            filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.webp"
            file_path = os.path.join(self.upload_dir, filename)
            
            # 儲存圖片
            processed_image.save(file_path, format='WEBP', quality=85, optimize=True)
            
            # 動態構建 URL
            if request_url:
                # 從請求 URL 獲取基礎 URL
                from urllib.parse import urlparse
                parsed_url = urlparse(request_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            else:
                base_url = self.base_url or "http://localhost:8001"
            
            avatar_url = f"{base_url}/static/avatars/{filename}"
            
            logger.info(f"頭像已儲存: {file_path}, URL: {avatar_url}")
            return avatar_url
            
        except Exception as e:
            logger.error(f"儲存頭像失敗: {str(e)}")
            raise ValueError(f"頭像處理失敗: {str(e)}")
    
    def delete_avatar(self, avatar_url: str) -> bool:
        """
        刪除頭像檔案
        
        Args:
            avatar_url: 頭像 URL
            
        Returns:
            bool: 是否成功刪除
        """
        try:
            # 從 URL 中提取檔案名稱
            filename = avatar_url.split('/')[-1]
            filepath = os.path.join(self.upload_dir, filename)
            
            # 檢查檔案是否存在並刪除
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Avatar file deleted: {filename}")
                return True
            else:
                logger.warning(f"Avatar file not found: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete avatar file: {e}")
            return False

# 全域頭像服務實例
avatar_service = AvatarService()
