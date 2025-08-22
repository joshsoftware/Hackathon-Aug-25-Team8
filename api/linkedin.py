from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from services.linkedin_scraper import LinkedInScraper
import asyncio
import json

router = APIRouter(prefix="/linkedin", tags=["LinkedIn Scraping"])

class LoginRequest(BaseModel):
    email: str
    password: str
    manual_login: bool = False

@router.post("/login")
async def login_to_linkedin(request: LoginRequest):
    """Login to LinkedIn with visual feedback"""
    scraper = LinkedInScraper()
    
    try:
        print(f"🔐 Starting LinkedIn login for {request.email}")
        await scraper.start_browser(headless=False, slow_mo=1000)
        
        if request.manual_login:
            login_success = await scraper.manual_login(request.email, request.password)
        else:
            login_success = await scraper.login(request.email, request.password)
        
        if login_success:
            return {
                "success": True,
                "message": "Successfully logged in to LinkedIn",
                "note": "Browser will remain open for further operations"
            }
        else:
            await scraper.close()
            raise HTTPException(status_code=401, detail="LinkedIn login failed")
        
    except Exception as e:
        await scraper.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "LinkedIn scraper is ready"}