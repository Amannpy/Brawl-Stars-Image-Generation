from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ArtStyle(str, Enum):
    CARTOON = "cartoon"
    REALISTIC = "realistic"
    ANIME = "anime"
    PIXEL_ART = "pixel_art"
    WATERCOLOR = "watercolor"
    COMIC = "comic"

class Theme(str, Enum):
    CYBERPUNK = "cyberpunk"
    MEDIEVAL = "medieval"
    SPACE = "space"
    UNDERWATER = "underwater"
    DESERT = "desert"
    JUNGLE = "jungle"
    PIRATE = "pirate"
    STEAMPUNK = "steampunk"

class GameMode(str, Enum):
    GEM_GRAB = "gem_grab"
    SHOWDOWN = "showdown"
    BRAWL_BALL = "brawl_ball"
    BOUNTY = "bounty"
    SIEGE = "siege"
    HOT_ZONE = "hot_zone"
    KNOCKOUT = "knockout"

class ImageGenerationRequest(BaseModel):
    brawler: str = Field(..., description="Name of the Brawl Stars character")
    theme: Theme = Field(..., description="Theme for the image")
    style: ArtStyle = Field(..., description="Art style for the image")
    mode: Optional[GameMode] = Field(None, description="Game mode setting")
    additional_prompt: Optional[str] = Field("", description="Additional prompt details")
    user_id: Optional[str] = Field("anonymous", description="User identifier")
    
    @validator('brawler')
    def validate_brawler_name(cls, v):
        return v.strip().title()
    
    @validator('additional_prompt')
    def validate_additional_prompt(cls, v):
        if v and len(v) > 500:
            raise ValueError("Additional prompt must be less than 500 characters")
        return v

class BatchGenerationRequest(BaseModel):
    requests: List[ImageGenerationRequest] = Field(..., max_items=5)
    
    @validator('requests')
    def validate_batch_size(cls, v):
        if len(v) > 5:
            raise ValueError("Maximum 5 requests per batch")
        return v

class GeneratedImage(BaseModel):
    url: str
    model: str
    cloudinary_url: Optional[str] = None
    metadata: Dict[str, Any]

class ImageGenerationResponse(BaseModel):
    success: bool
    generation_id: str
    images: List[GeneratedImage]
    prompt_used: str
    generation_time_ms: int
    total_images: int
    created_at: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
    timestamp: datetime