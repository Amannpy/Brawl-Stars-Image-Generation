import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.core.database import db_manager
from app.models.schemas import BrawlerModel

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=1)
        self.last_cache_update = {}
    
    async def get_brawler(self, name: str) -> Optional[Dict[str, Any]]:
        """Get brawler information from knowledge base"""
        cache_key = f"brawler_{name.lower()}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Query database
        brawler = await db_manager.database.brawlers.find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}}
        )
        
        if brawler:
            # Remove MongoDB ObjectId
            brawler.pop('_id', None)
            self.cache[cache_key] = brawler
            self.last_cache_update[cache_key] = datetime.now()
        
        return brawler
    
    async def get_game_mode(self, mode: str) -> Optional[Dict[str, Any]]:
        """Get game mode information"""
        cache_key = f"mode_{mode.lower()}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        game_mode = await db_manager.database.game_modes.find_one(
            {"name": {"$regex": f"^{mode.replace('_', ' ')}$", "$options": "i"}}
        )
        
        if game_mode:
            game_mode.pop('_id', None)
            self.cache[cache_key] = game_mode
            self.last_cache_update[cache_key] = datetime.now()
        
        return game_mode
    
    async def get_popular_combinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular brawler/theme combinations"""
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "brawler": "$user_input.brawler",
                        "theme": "$user_input.theme"
                    },
                    "count": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = await db_manager.database.generation_history.aggregate(pipeline).to_list(limit)
        return results
    
    async def update_brawler_data(self, brawler_data: Dict[str, Any]) -> bool:
        """Update or insert brawler data"""
        try:
            await db_manager.database.brawlers.update_one(
                {"name": brawler_data["name"]},
                {"$set": {**brawler_data, "updated_at": datetime.now()}},
                upsert=True
            )
            
            # Invalidate cache
            cache_key = f"brawler_{brawler_data['name'].lower()}"
            self.cache.pop(cache_key, None)
            
            return True
        except Exception as e:
            logger.error(f"Error updating brawler data: {e}")
            return False
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        last_update = self.last_cache_update.get(cache_key)
        if not last_update:
            return False
        
        return datetime.now() - last_update < self.cache_ttl

# Global instance
knowledge_base = KnowledgeBaseService()