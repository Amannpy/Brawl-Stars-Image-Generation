import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.database import Brawler, PromptTemplate
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class PromptEnhancer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.db = SessionLocal()
    
    async def enhance_prompt(self, user_prompt: str) -> str:
        """
        Enhance a user prompt with game-specific knowledge.
        """
        try:
            # Extract entities from the prompt
            entities = await self._extract_entities(user_prompt)
            
            # Get relevant context for each entity
            context = await self._get_relevant_context(entities)
            
            # Find a suitable template
            template = await self._find_template(user_prompt, context)
            
            # Build the enhanced prompt
            enhanced_prompt = await self._build_enhanced_prompt(
                user_prompt,
                template,
                context
            )
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return user_prompt  # Return original prompt if enhancement fails
    
    async def _extract_entities(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Extract Brawl Stars entities (brawlers, game modes, etc.) from the prompt.
        """
        # Get all brawlers
        brawlers = self.db.query(Brawler).all()
        
        # Find mentions of brawlers in the prompt
        entities = []
        for brawler in brawlers:
            if brawler.name.lower() in prompt.lower():
                entities.append({
                    "type": "brawler",
                    "name": brawler.name,
                    "data": brawler
                })
        
        return entities
    
    async def _get_relevant_context(
        self,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get relevant context for the extracted entities.
        """
        context = {
            "brawlers": [],
            "game_modes": [],
            "themes": []
        }
        
        for entity in entities:
            if entity["type"] == "brawler":
                brawler = entity["data"]
                context["brawlers"].append({
                    "name": brawler.name,
                    "description": brawler.description,
                    "attack": brawler.attack_description,
                    "super": brawler.super_description,
                    "visual": brawler.visual_characteristics
                })
        
        return context
    
    async def _find_template(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> PromptTemplate:
        """
        Find a suitable template for the prompt.
        """
        # Get all templates
        templates = self.db.query(PromptTemplate).all()
        
        # Convert prompt and templates to embeddings
        prompt_embedding = self.model.encode(prompt)
        template_embeddings = {
            t.id: self.model.encode(t.template)
            for t in templates
        }
        
        # Find the most similar template
        best_template = None
        best_similarity = -1
        
        for template_id, embedding in template_embeddings.items():
            similarity = np.dot(prompt_embedding, embedding) / (
                np.linalg.norm(prompt_embedding) * np.linalg.norm(embedding)
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_template = next(
                    t for t in templates if t.id == template_id
                )
        
        return best_template or templates[0]  # Fallback to first template
    
    async def _build_enhanced_prompt(
        self,
        original_prompt: str,
        template: PromptTemplate,
        context: Dict[str, Any]
    ) -> str:
        """
        Build the enhanced prompt using the template and context.
        """
        # Replace template placeholders with context
        enhanced = template.template
        
        # Add brawler details
        for brawler in context["brawlers"]:
            enhanced = enhanced.replace(
                f"{{brawler_{brawler['name'].lower()}}}",
                f"{brawler['name']}, {brawler['description']}"
            )
        
        # Add the original prompt
        enhanced = enhanced.replace("{original_prompt}", original_prompt)
        
        return enhanced 