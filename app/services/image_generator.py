import asyncio
import httpx
import openai
from typing import List, Dict, Any, Tuple
import time
import logging
from app.config import settings
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.replicate_token = settings.REPLICATE_API_TOKEN
    
    async def generate_images(
        self, 
        enhanced_prompt: str,
        generation_id: str
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Generate images using multiple AI models"""
        
        start_time = time.time()
        
        # Generate with multiple models concurrently
        tasks = [
            self._generate_dalle3(enhanced_prompt),
            self._generate_stable_diffusion(enhanced_prompt)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        images = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Generation failed for model {i}: {result}")
                continue
            
            if result:
                images.extend(result)
        
        # Upload to cloud storage
        for image in images:
            try:
                cloud_url = await storage_service.upload_image(
                    image["url"], 
                    generation_id,
                    {
                        "model": image["model"],
                        "generation_id": generation_id
                    }
                )
                image["cloudinary_url"] = cloud_url
            except Exception as e:
                logger.error(f"Failed to upload image: {e}")
        
        generation_time = int((time.time() - start_time) * 1000)  # Convert to ms
        
        return images, generation_time
    
    async def _generate_dalle3(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate image using DALL-E 3"""
        try:
            response = await openai.Image.acreate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                style="vivid",
                n=1
            )
            
            images = []
            for image_data in response.data:
                images.append({
                    "url": image_data.url,
                    "model": "dall-e-3",
                    "revised_prompt": getattr(image_data, 'revised_prompt', None),
                    "metadata": {
                        "model": "dall-e-3",
                        "size": "1024x1024",
                        "quality": "hd"
                    }
                })
            
            return images
            
        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            return []
    
    async def _generate_stable_diffusion(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate image using Stable Diffusion via Replicate"""
        try:
            async with httpx.AsyncClient() as client:
                # Start prediction
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {self.replicate_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
                        "input": {
                            "prompt": prompt,
                            "width": 1024,
                            "height": 1024,
                            "num_inference_steps": 20,
                            "guidance_scale": 7.5,
                            "scheduler": "K_EULER"
                        }
                    }
                )
                
                if response.status_code != 201:
                    logger.error(f"Replicate API error: {response.status_code}")
                    return []
                
                prediction = response.json()
                prediction_id = prediction["id"]
                
                # Poll for completion
                max_attempts = 60  # 5 minutes max
                for _ in range(max_attempts):
                    status_response = await client.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {self.replicate_token}"}
                    )
                    
                    if status_response.status_code != 200:
                        break
                    
                    status_data = status_response.json()
                    
                    if status_data["status"] == "succeeded":
                        if status_data["output"]:
                            return [{
                                "url": status_data["output"][0],
                                "model": "stable-diffusion",
                                "metadata": {
                                    "model": "stable-diffusion",
                                    "size": "1024x1024",
                                    "steps": 20
                                }
                            }]
                        break
                    elif status_data["status"] == "failed":
                        logger.error(f"Stable Diffusion failed: {status_data.get('error')}")
                        break
                    
                    await asyncio.sleep(5)  # Wait 5 seconds before next poll
                
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}")
        
        return []

# Global instance
image_generator = ImageGenerator()