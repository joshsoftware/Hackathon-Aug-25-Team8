from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from services.linkedin_scraper import LinkedInScraper
import asyncio
import json
from datetime import datetime

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

class JobSearchRequest(BaseModel):
    email: str
    password: str
    job_title: str
    max_jobs: int = 10
    search_method: str = "direct_url"  # "feed", "direct", or "direct_url"

@router.post("/jobs")
async def search_jobs(request: JobSearchRequest):
    """Search jobs from LinkedIn using specified method"""
    scraper = LinkedInScraper()
    
    try:
        print(f"🚀 Starting job search for: {request.job_title} using {request.search_method} method")
        await scraper.start_browser(headless=False, slow_mo=1000)
        
        # Use the appropriate search method
        if request.search_method == "direct_url":
            jobs = await scraper.search_jobs_direct_url(
                email=request.email,
                password=request.password,
                job_title=request.job_title,
                max_jobs=request.max_jobs
            )
        elif request.search_method == "direct":
            jobs = await scraper.search_jobs_direct(
                email=request.email,
                password=request.password,
                job_title=request.job_title,
                max_jobs=request.max_jobs
            )
        else:
            jobs = await scraper.search_jobs_from_feed(
                email=request.email,
                password=request.password,
                job_title=request.job_title,
                max_jobs=request.max_jobs
            )
        
        await scraper.close()
        
        if jobs:
            return {
                "success": True,
                "message": f"Successfully scraped {len(jobs)} jobs from LinkedIn jobs search page",
                "data": jobs,
                "search_params": {
                    "job_title": request.job_title,
                    "max_jobs": request.max_jobs,
                    "search_method": request.search_method
                }
            }
        else:
            return {
                "success": False,
                "message": "No jobs found. Please check your search criteria or try different keywords.",
                "data": [],
                "search_params": {
                    "job_title": request.job_title,
                    "max_jobs": request.max_jobs,
                    "search_method": request.search_method
                }
            }
        
    except Exception as e:
        await scraper.close()
        raise HTTPException(status_code=500, detail=str(e))