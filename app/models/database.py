from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, TEXT
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import asyncio

class BrawlerModel(BaseModel):
    name: str
    type: str
    rarity: str
    description: str
    abilities: List[str]
    personality: str
    visual_style: str
    keywords: List[str]
    created_at: datetime
    updated_at: datetime

class GameModeModel(BaseModel):
    name: str
    description: str
    setting: str
    keywords: List[str]
    strategies: List[str]
    created_at: datetime

class GenerationHistoryModel(BaseModel):
    generation_id: str
    user_input: Dict[str, Any]
    enhanced_prompt: str
    images: List[Dict[str, Any]]
    success: bool
    error_message: Optional[str] = None
    generation_time_ms: int
    created_at: datetime

class DatabaseManager:
    def __init__(self, connection_string: str, database_name: str):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
        self.connection_string = connection_string
        self.database_name = database_name
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.connection_string)
        self.database = self.client[self.database_name]
        await self.create_indexes()
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def create_indexes(self):
        """Create database indexes for performance"""
        collections_indexes = {
            "brawlers": [
                IndexModel([("name", ASCENDING)], unique=True),
                IndexModel([("type", ASCENDING)]),
                IndexModel([("keywords", ASCENDING)])
            ],
            "game_modes": [
                IndexModel([("name", ASCENDING)], unique=True)
            ],
            "generation_history": [
                IndexModel([("generation_id", ASCENDING)], unique=True),
                IndexModel([("created_at", ASCENDING)]),
                IndexModel([("user_input.brawler", ASCENDING)])
            ],
            "community_trends": [
                IndexModel([("created_at", ASCENDING)]),
                IndexModel([("keywords", ASCENDING)])
            ]
        }
        
        for collection_name, indexes in collections_indexes.items():
            collection = self.database[collection_name]
            await collection.create_indexes(indexes)

# Global database instance
db_manager = DatabaseManager("", "")