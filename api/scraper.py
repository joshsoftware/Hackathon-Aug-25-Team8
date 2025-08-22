from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio
import logging

from models.scraper_models import ScrapeRequest, ScrapeResponse
from services.scraper_service import WebScraper

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape a website with authentication and optional filters
    
    Args:
        request: ScrapeRequest containing URL, credentials, and filters
        background_tasks: FastAPI background tasks for async processing
        
    Returns:
        ScrapeResponse with scraped data or error information
    """
    try:
        # Prepare filters dictionary
        filters = {}
        if request.search_filter:
            filters["search"] = request.search_filter
        if request.category_filter:
            filters["category"] = request.category_filter
        if request.data_types and request.data_types != ["all"]:
            filters["data_types"] = [dt.value for dt in request.data_types]
        
        # Use the scraper service
        async with WebScraper() as scraper:
            result = await scraper.scrape_website(
                url=str(request.url),
                username=request.username or "",
                password=request.password or "",
                filters=filters if filters else None
            )
        
        return ScrapeResponse(**result)
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )

@router.get("/scrape/health")
async def scraper_health_check():
    """
    Health check endpoint for the scraper service
    """
    return {
        "status": "healthy",
        "service": "web_scraper",
        "message": "Scraper service is running"
    }

@router.post("/scrape/batch")
async def scrape_multiple_websites(requests: list[ScrapeRequest]):
    """
    Scrape multiple websites in batch
    
    Args:
        requests: List of ScrapeRequest objects
        
    Returns:
        List of ScrapeResponse objects
    """
    try:
        results = []
        
        for request in requests:
            try:
                # Prepare filters for each request
                filters = {}
                if request.search_filter:
                    filters["search"] = request.search_filter
                if request.category_filter:
                    filters["category"] = request.category_filter
                if request.data_types and request.data_types != ["all"]:
                    filters["data_types"] = [dt.value for dt in request.data_types]
                
                # Scrape each website
                async with WebScraper() as scraper:
                    result = await scraper.scrape_website(
                        url=str(request.url),
                        username=request.username or "",
                        password=request.password or "",
                        filters=filters if filters else None
                    )
                
                results.append(ScrapeResponse(**result))
                
            except Exception as e:
                logger.error(f"Batch scraping failed for {request.url}: {str(e)}")
                results.append(ScrapeResponse(
                    success=False,
                    url=str(request.url),
                    timestamp="",
                    error=str(e)
                ))
        
        return {
            "total_requests": len(requests),
            "successful": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch scraping failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch scraping failed: {str(e)}"
        )

