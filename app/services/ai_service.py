import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.database import GeneratedImage
from app.core.config import settings
import openai
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk import client

logger = logging.getLogger(__name__)

class AIImageService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.stability_client = client.StabilityInference(
            key=settings.STABILITY_API_KEY,
            verbose=True,
        )
    
    async def generate_image(
        self,
        generation_id: str,
        prompt: str,
        style_params: Dict[str, Any]
    ) -> None:
        """
        Generate an image using the best available provider.
        """
        db = SessionLocal()
        try:
            # Try OpenAI first
            try:
                image_url = await self._generate_with_openai(prompt, style_params)
            except Exception as e:
                logger.warning(f"OpenAI generation failed: {e}")
                # Fallback to Stability AI
                try:
                    image_url = await self._generate_with_stability(prompt, style_params)
                except Exception as e:
                    logger.error(f"Stability AI generation failed: {e}")
                    raise Exception("All image generation providers failed")
            
            # Update the generation record
            generation = db.query(GeneratedImage).filter(
                GeneratedImage.id == generation_id
            ).first()
            if generation:
                generation.image_url = image_url
                db.commit()
                
        finally:
            db.close()
    
    async def _generate_with_openai(
        self,
        prompt: str,
        style_params: Dict[str, Any]
    ) -> str:
        """
        Generate an image using OpenAI's DALL-E.
        """
        response = await self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=style_params.get("size", "1024x1024"),
            quality=style_params.get("quality", "standard"),
            n=1,
        )
        return response.data[0].url
    
    async def _generate_with_stability(
        self,
        prompt: str,
        style_params: Dict[str, Any]
    ) -> str:
        """
        Generate an image using Stability AI.
        """
        # Convert style parameters to Stability AI format
        stability_params = {
            "steps": 30,
            "cfg_scale": 7.0,
            "width": 1024,
            "height": 1024,
            "samples": 1,
            "style_preset": style_params.get("style", "digital-art"),
        }
        
        # Add negative prompt if provided
        if style_params.get("negative_prompt"):
            stability_params["negative_prompt"] = style_params["negative_prompt"]
        
        # Generate the image
        answers = self.stability_client.generate(
            prompt=prompt,
            **stability_params
        )
        
        # Process the response
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.type == generation.ARTIFACT_IMAGE:
                    # Save the image and return the URL
                    # This is a placeholder - you'll need to implement actual image storage
                    return f"https://storage.example.com/images/{artifact.finish_reason}.png"
        
        raise Exception("No image was generated") 