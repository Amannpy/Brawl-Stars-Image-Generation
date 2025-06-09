import cloudinary
import cloudinary.uploader
from typing import Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
    
    async def upload_image(
        self, 
        image_url: str, 
        generation_id: str,
        metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Upload image to Cloudinary and return public URL"""
        
        try:
            upload_result = cloudinary.uploader.upload(
                image_url,
                folder="brawl-stars-generated",
                public_id=f"{generation_id}_{metadata.get('model', 'unknown')}",
                tags=["brawl-stars", "ai-generated", metadata.get('model', 'unknown')],
                context=metadata,
                resource_type="image"
            )
            
            return upload_result.get("secure_url")
            
        except Exception as e:
            logger.error(f"Failed to upload image to Cloudinary: {e}")
            return None

# Global instance
storage_service = StorageService()