"""
靜態檔案服務路由

提供上傳的頭像圖片訪問服務
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

AVATAR_DIR = "uploads/avatars"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    """
    獲取頭像圖片
    
    Args:
        filename: 圖片檔案名稱
        
    Returns:
        FileResponse: 圖片檔案回應
    """
    try:
        # 驗證檔案名稱
        if not filename or '..' in filename or '/' in filename:
            raise HTTPException(status_code=400, detail="無效的檔案名稱")
        
        # 檢查副檔名
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="不支援的檔案格式")
        
        # 建構檔案路徑
        file_path = os.path.join(AVATAR_DIR, filename)
        
        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            logger.warning(f"Avatar file not found: {filename}")
            raise HTTPException(status_code=404, detail="頭像檔案不存在")
        
        # 檢查是否為檔案（非目錄）
        if not os.path.isfile(file_path):
            logger.warning(f"Invalid file path: {filename}")
            raise HTTPException(status_code=400, detail="無効的檔案路徑")
        
        # 根據副檔名設定媒體類型
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(file_ext, 'application/octet-stream')
        
        logger.info(f"Serving avatar file: {filename}")
        return FileResponse(
            path=file_path,
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # 快取 24 小時
                "Content-Disposition": f"inline; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving avatar {filename}: {e}")
        raise HTTPException(status_code=500, detail="檔案服務錯誤")
