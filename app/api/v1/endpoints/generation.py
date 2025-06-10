from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, GeneratedImage
from app.schemas.generation import GenerationRequest, GenerationResponse
from app.services.ai_service import AIImageService
from app.services.prompt_enhancer import PromptEnhancer

router = APIRouter()
ai_service = AIImageService()
prompt_enhancer = PromptEnhancer()

@router.post("/", response_model=GenerationResponse)
async def generate_image(
    *,
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Generate an image based on the provided prompt.
    """
    # Enhance the prompt with game-specific knowledge
    enhanced_prompt = await prompt_enhancer.enhance_prompt(request.prompt)
    
    # Create a new generation record
    generation = GeneratedImage(
        user_id=current_user.id,
        original_prompt=request.prompt,
        enhanced_prompt=enhanced_prompt,
        generation_params=request.style_params.dict(),
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    # Queue the generation task
    background_tasks.add_task(
        ai_service.generate_image,
        generation.id,
        enhanced_prompt,
        request.style_params.dict(),
    )
    
    return GenerationResponse(
        task_id=str(generation.id),
        status="queued",
        message="Image generation has been queued"
    )

@router.get("/{task_id}", response_model=GenerationResponse)
async def get_generation_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the status of an image generation task.
    """
    generation = db.query(GeneratedImage).filter(
        GeneratedImage.id == task_id,
        GeneratedImage.user_id == current_user.id
    ).first()
    
    if not generation:
        raise HTTPException(
            status_code=404,
            detail="Generation task not found"
        )
    
    return GenerationResponse(
        task_id=str(generation.id),
        status="completed" if generation.image_url else "processing",
        image_url=generation.image_url,
        message="Image generation completed" if generation.image_url else "Image generation in progress"
    ) 