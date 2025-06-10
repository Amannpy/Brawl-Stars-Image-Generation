from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class StyleParams(BaseModel):
    style: str = Field(default="brawl_stars", description="Art style to use")
    size: str = Field(default="1024x1024", description="Image dimensions")
    quality: str = Field(default="standard", description="Generation quality")
    negative_prompt: Optional[str] = Field(default=None, description="Elements to avoid in generation")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional style parameters")

class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="The main prompt for image generation")
    style_params: StyleParams = Field(default_factory=StyleParams, description="Style parameters for generation")

class GenerationResponse(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the generation task")
    status: str = Field(..., description="Current status of the generation task")
    message: str = Field(..., description="Status message")
    image_url: Optional[str] = Field(None, description="URL of the generated image (if completed)") 