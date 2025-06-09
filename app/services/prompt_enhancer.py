import openai
from typing import Dict, Any, Optional
import logging
from app.config import settings
from app.services.knowledge_base import knowledge_base

logger = logging.getLogger(__name__)

class PromptEnhancer:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.base_prompt_templates = {
            "cartoon": "Create a vibrant cartoon-style digital artwork",
            "realistic": "Create a photorealistic digital artwork",
            "anime": "Create an anime-style digital artwork",
            "pixel_art": "Create a pixel art style digital artwork",
            "watercolor": "Create a watercolor painting style artwork",
            "comic": "Create a comic book style digital artwork"
        }
    
    async def enhance_prompt(
        self, 
        user_request: Dict[str, Any]
    ) -> str:
        """Enhance user prompt with knowledge base data"""
        
        # Get brawler data
        brawler_data = await knowledge_base.get_brawler(user_request["brawler"])
        if not brawler_data:
            raise ValueError(f"Brawler '{user_request['brawler']}' not found in knowledge base")
        
        # Get game mode data if specified
        mode_data = None
        if user_request.get("mode"):
            mode_data = await knowledge_base.get_game_mode(user_request["mode"])
        
        # Build enhanced prompt
        enhanced_prompt = self._build_enhanced_prompt(
            user_request, brawler_data, mode_data
        )
        
        # Use AI to further refine the prompt
        refined_prompt = await self._ai_refine_prompt(enhanced_prompt, user_request)
        
        return refined_prompt
    
    def _build_enhanced_prompt(
        self, 
        user_request: Dict[str, Any],
        brawler_data: Dict[str, Any],
        mode_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build enhanced prompt from knowledge base"""
        
        style_template = self.base_prompt_templates.get(
            user_request["style"], 
            "Create a digital artwork"
        )
        
        prompt_parts = [
            f"{style_template} of {brawler_data['name']},",
            f"a {brawler_data['type']} type brawler.",
            f"Character description: {brawler_data['description']}",
            f"Personality: {brawler_data['personality']}",
            f"Visual characteristics: {brawler_data['visual_style']}",
            f"Key visual elements: {', '.join(brawler_data['keywords'])}",
            f"Theme: {user_request['theme']} aesthetic",
        ]
        
        if mode_data:
            prompt_parts.extend([
                f"Setting: {mode_data['description']} environment",
                f"Environment details: {mode_data['setting']}"
            ])
        
        if user_request.get("additional_prompt"):
            prompt_parts.append(f"Additional requirements: {user_request['additional_prompt']}")
        
        # Technical requirements
        prompt_parts.extend([
            "Technical requirements:",
            "- High resolution (1024x1024)",
            "- Professional digital art quality",
            "- Vibrant colors and dynamic composition",
            "- Consistent with Brawl Stars art style",
            "- Dramatic lighting and engaging pose"
        ])
        
        return " ".join(prompt_parts)
    
    async def _ai_refine_prompt(
        self, 
        base_prompt: str, 
        user_request: Dict[str, Any]
    ) -> str:
        """Use AI to refine and optimize the prompt"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert prompt engineer for AI image generation. "
                                 "Optimize prompts for creating high-quality Brawl Stars character artwork. "
                                 "Keep the core information but make it more concise and effective for image generation."
                    },
                    {
                        "role": "user",
                        "content": f"Optimize this image generation prompt while keeping all important details:\n\n{base_prompt}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            return refined_prompt
            
        except Exception as e:
            logger.warning(f"AI prompt refinement failed: {e}. Using base prompt.")
            return base_prompt

# Global instance
prompt_enhancer = PromptEnhancer()