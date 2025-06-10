from fastapi import APIRouter

from app.api.v1.endpoints import auth, generation, brawlers, gallery, prompts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(generation.router, prefix="/generate", tags=["image generation"])
api_router.include_router(brawlers.router, prefix="/brawlers", tags=["brawlers"])
api_router.include_router(gallery.router, prefix="/gallery", tags=["community gallery"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompt suggestions"]) 