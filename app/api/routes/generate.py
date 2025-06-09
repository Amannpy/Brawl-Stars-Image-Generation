from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List
import uuid
import time
from datetime import datetime
import logging

from app.models.schemas import (
    ImageGenerationRequest, 
    BatchGenerationRequest,
    ImageGenerationResponse,
    ErrorResponse
)
from app.services.prompt_enhancer import prompt_enhancer
from app.services.image_generator import image_generator
from app.core.database import db_manager
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/single", response_model=ImageGenerationResponse)
async def generate_single_image(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate a single image based on the request"""
    
    generation_id = generate_id()
    start_time = time.time()
    
    try:
        # Enhance prompt using knowledge base
        enhanced_prompt = await prompt_enhancer.enhance_prompt(request.dict())
        
        # Generate images
        images, generation_time = await image_generator.generate_images(
            enhanced_prompt, generation_id
        )
        
        if not images:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate any images"
            )
        
        # Prepare response
        response = ImageGenerationResponse(
            success=True,
            generation_id=generation_id,
            images=images,
            prompt_used=enhanced_prompt,
            generation_time_ms=generation_time,
            total_images=len(images),
            created_at=datetime.now()
        )
        
        # Save to database in background
        background_tasks.add_task(
            save_generation_history,
            generation_id,
            request.dict(),
            enhanced_prompt,
            images,
            True,
            None,
            generation_time
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        
        # Save error to database
        background_tasks.add_task(
            save_generation_history,
            generation_id,
            request.dict(),
            "",
            [],
            False,
            str(e),
            int((time.time() - start_time) * 1000)
        )
        
        raise HTTPException(
            status_code=500,
            detail="Image generation failed"
        )

@router.post("/batch", response_model=List[ImageGenerationResponse])
async def generate_batch_images(
    request: BatchGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate multiple images in batch"""
    
    results = []
    
    for individual_request in request.requests:
        try:
            result = await generate_single_image(individual_request, background_tasks)
            results.append(result)