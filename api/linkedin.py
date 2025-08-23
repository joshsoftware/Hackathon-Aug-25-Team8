from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.linkedin_scraper import LinkedInScraper
import asyncio
import json
from datetime import datetime
import time
import os

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

# Global storage for job details
job_details_cache = {}

@router.post("/jobs")
async def search_jobs(request: JobSearchRequest, background_tasks: BackgroundTasks):
    """Search jobs from LinkedIn using specified method and automatically start background crawling"""
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
            # Create a unique search ID for this batch of jobs
            search_id = f"search_{int(time.time())}"
            
            # Extract job URLs for background crawling
            job_urls = []
            
            # Store the jobs in the cache with their URLs as keys
            for job in jobs:
                if job.get('url'):
                    job_url = job['url']
                    job_urls.append(job_url)
                    job_details_cache[job_url] = {
                        'basic_info': job,
                        'detailed_info': None,
                        'search_id': search_id,
                        'status': 'pending'
                    }
            
            # Automatically start background crawling of job details
            if job_urls:
                print(f"🔄 Automatically starting background crawling for {len(job_urls)} job URLs")
                background_tasks.add_task(
                    crawl_job_details_background,
                    request.email,
                    request.password,
                    job_urls
                )
            
            return {
                "success": True,
                "message": f"Successfully scraped {len(jobs)} jobs from LinkedIn jobs search page. Background crawling started automatically.",
                "data": jobs,
                "search_id": search_id,
                "background_crawling": {
                    "status": "started",
                    "job_urls": len(job_urls),
                    "message": "Detailed job information is being crawled in the background. Use the /job-details/{search_id} endpoint to check progress and retrieve detailed data."
                },
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

class JobDetailRequest(BaseModel):
    email: str
    password: str
    job_urls: List[str]
    
async def crawl_job_details_background(email: str, password: str, job_urls: List[str]):
    """Background task to crawl job details from multiple URLs"""
    try:
        print(f"🚀 Starting background crawling of {len(job_urls)} job URLs")
        
        # Start a new browser instance
        scraper = LinkedInScraper()
        await scraper.start_browser(headless=True)  # Use headless mode for background tasks
        
        # Login to LinkedIn
        login_success = await scraper.login(email, password)
        if not login_success:
            print("❌ Login failed in background task")
            await scraper.close()
            return
        
        # Process each job URL
        for job_url in job_urls:
            try:
                print(f"🔍 Processing job URL in background: {job_url}")
                
                # Update status to 'processing'
                if job_url in job_details_cache:
                    job_details_cache[job_url]['status'] = 'processing'
                
                # Scrape detailed job information
                job_detail = await scraper.scrape_job_details(job_url)
                
                # Store the detailed information in the cache
                if job_url in job_details_cache:
                    job_details_cache[job_url]['detailed_info'] = job_detail
                    job_details_cache[job_url]['status'] = 'completed'
                    print(f"✅ Successfully scraped and stored details for job: {job_detail.get('title', 'Unknown')}")
                else:
                    # If the URL wasn't in the cache, add it
                    job_details_cache[job_url] = {
                        'basic_info': None,
                        'detailed_info': job_detail,
                        'search_id': 'manual',
                        'status': 'completed'
                    }
                    print(f"✅ Added new job details to cache: {job_detail.get('title', 'Unknown')}")
                
                # Small delay between requests to avoid rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing job URL {job_url}: {str(e)}")
                if job_url in job_details_cache:
                    job_details_cache[job_url]['status'] = 'failed'
                    job_details_cache[job_url]['error'] = str(e)
        
        # Close the browser when done
        await scraper.close()
        print("✅ Background job crawling completed")
        
    except Exception as e:
        print(f"❌ Background task error: {str(e)}")

@router.post("/crawl-job-details")
async def crawl_job_details(request: JobDetailRequest, background_tasks: BackgroundTasks):
    """Start background crawling of job details from provided URLs"""
    try:
        # Validate job URLs
        valid_urls = [url for url in request.job_urls if url and 'linkedin.com' in url]
        
        if not valid_urls:
            return {
                "success": False,
                "message": "No valid LinkedIn job URLs provided"
            }
        
        # Add the background task
        background_tasks.add_task(
            crawl_job_details_background,
            request.email,
            request.password,
            valid_urls
        )
        
        # Initialize cache entries for these URLs if they don't exist
        for url in valid_urls:
            if url not in job_details_cache:
                job_details_cache[url] = {
                    'basic_info': None,
                    'detailed_info': None,
                    'search_id': 'manual',
                    'status': 'pending'
                }
        
        return {
            "success": True,
            "message": f"Started background crawling of {len(valid_urls)} job URLs",
            "job_urls": valid_urls
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-details/{search_id}")
async def get_job_details(search_id: str):
    """Get all job details for a specific search ID"""
    try:
        # Filter jobs by search ID
        search_jobs = {
            url: details for url, details in job_details_cache.items()
            if details.get('search_id') == search_id
        }
        
        if not search_jobs:
            return {
                "success": False,
                "message": f"No jobs found for search ID: {search_id}"
            }
        
        # Count jobs by status
        status_counts = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0
        }
        
        for job_url, details in search_jobs.items():
            status = details.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
        
        # Prepare the response data
        jobs_data = []
        for job_url, details in search_jobs.items():
            job_data = {
                'url': job_url,
                'status': details.get('status', 'unknown')
            }
            
            # Include basic info if available
            if details.get('basic_info'):
                job_data.update(details['basic_info'])
            
            # Include detailed info if available
            if details.get('detailed_info'):
                # If there's overlap between basic and detailed info, detailed takes precedence
                job_data.update(details['detailed_info'])
            
            # Add error if present
            if details.get('error'):
                job_data['error'] = details['error']
                
            jobs_data.append(job_data)
        
        return {
            "success": True,
            "message": f"Found {len(search_jobs)} jobs for search ID: {search_id}",
            "status_summary": status_counts,
            "data": jobs_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-details-url")
async def get_job_details_by_url(url: str):
    """Get job details for a specific URL"""
    try:
        if url not in job_details_cache:
            return {
                "success": False,
                "message": f"No job details found for URL: {url}"
            }
        
        details = job_details_cache[url]
        
        # Prepare the response data
        job_data = {
            'url': url,
            'status': details.get('status', 'unknown')
        }
        
        # Include basic info if available
        if details.get('basic_info'):
            job_data.update(details['basic_info'])
        
        # Include detailed info if available
        if details.get('detailed_info'):
            # If there's overlap between basic and detailed info, detailed takes precedence
            job_data.update(details['detailed_info'])
        
        # Add error if present
        if details.get('error'):
            job_data['error'] = details['error']
        
        return {
            "success": True,
            "message": f"Found job details for URL: {url}",
            "data": job_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CompanySearchRequest(BaseModel):
    email: str
    password: str
    company_name: str
    max_companies: int = 10

class CompanyDetailRequest(BaseModel):
    email: str
    password: str
    company_urls: List[str]

# Global storage for company details
company_details_cache = {}

@router.post("/companies")
async def search_companies(request: CompanySearchRequest, background_tasks: BackgroundTasks):
    """Search companies from LinkedIn feed page and automatically start background crawling for detailed info"""
    scraper = LinkedInScraper()
    
    try:
        print(f"🚀 Starting company search for: {request.company_name}")
        await scraper.start_browser(headless=False, slow_mo=1000)
        
        # Search for companies
        companies = await scraper.search_companies(
            email=request.email,
            password=request.password,
            company_name=request.company_name,
            max_companies=request.max_companies
        )
        
        await scraper.close()
        
        if companies:
            # Create a unique search ID for this batch of companies
            search_id = f"company_search_{int(time.time())}"
            
            # Extract company URLs for background crawling
            company_urls = []
            
            # Store the companies in the cache with their URLs as keys
            for company in companies:
                if company.get('url'):
                    company_url = company['url']
                    company_urls.append(company_url)
                    company_details_cache[company_url] = {
                        'basic_info': company,
                        'detailed_info': None,
                        'search_id': search_id,
                        'status': 'pending'
                    }
            
            # Automatically start background crawling of company details
            if company_urls:
                print(f"🔄 Automatically starting background crawling for {len(company_urls)} company URLs")
                background_tasks.add_task(
                    crawl_company_details_background,
                    request.email,
                    request.password,
                    company_urls
                )
            
            return {
                "success": True,
                "message": f"Successfully scraped {len(companies)} companies from LinkedIn. Background crawling started automatically.",
                "data": companies,
                "search_id": search_id,
                "background_crawling": {
                    "status": "started",
                    "company_urls": len(company_urls),
                    "message": "Detailed company information is being crawled in the background. Use the /company-details/{search_id} endpoint to check progress and retrieve detailed data."
                },
                "search_params": {
                    "company_name": request.company_name,
                    "max_companies": request.max_companies
                }
            }
        else:
            return {
                "success": False,
                "message": "No companies found. Please check your search criteria or try different keywords.",
                "data": [],
                "search_params": {
                    "company_name": request.company_name,
                    "max_companies": request.max_companies
                }
            }
        
    except Exception as e:
        await scraper.close()
        raise HTTPException(status_code=500, detail=str(e))

async def crawl_company_details_background(email: str, password: str, company_urls: List[str]):
    """Background task to crawl company details from multiple URLs"""
    try:
        # Add longer sleep to ensure previous operations are complete
        time.sleep(8)
        print(f"🚀 Starting background crawling of {len(company_urls)} company URLs")
        
        # Start a new browser instance
        scraper = LinkedInScraper()
        await scraper.start_browser(headless=True)  # Use headless mode for background tasks
        
        # Login to LinkedIn
        login_success = await scraper.login(email, password)
        if not login_success:
            print("❌ Login failed in background task")
            await scraper.close()
            return
        
        # Process each company URL
        for company_url in company_urls:
            try:
                print(f"🔍 Processing company URL in background: {company_url}")
                
                # Update status to 'processing'
                if company_url in company_details_cache:
                    company_details_cache[company_url]['status'] = 'processing'
                
                # Scrape detailed company information
                company_detail = await scraper.scrape_company_details(company_url)
                
                # Store the detailed information in the cache
                if company_url in company_details_cache:
                    company_details_cache[company_url]['detailed_info'] = company_detail
                    company_details_cache[company_url]['status'] = 'completed'
                    print(f"✅ Successfully scraped and stored details for company: {company_detail.get('name', 'Unknown')}")
                else:
                    # If the URL wasn't in the cache, add it
                    company_details_cache[company_url] = {
                        'basic_info': None,
                        'detailed_info': company_detail,
                        'search_id': 'manual',
                        'status': 'completed'
                    }
                    print(f"✅ Added new company details to cache: {company_detail.get('name', 'Unknown')}")
                
                # Longer delay between requests to avoid rate limiting and ensure complete loading
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ Error processing company URL {company_url}: {str(e)}")
                if company_url in company_details_cache:
                    company_details_cache[company_url]['status'] = 'failed'
                    company_details_cache[company_url]['error'] = str(e)
        
        # Close the browser when done
        await scraper.close()
        print("✅ Background company crawling completed")
        
    except Exception as e:
        print(f"❌ Background task error: {str(e)}")

@router.post("/crawl-company-details")
async def crawl_company_details(request: CompanyDetailRequest, background_tasks: BackgroundTasks):
    """Start background crawling of company details from provided URLs"""
    try:
        # Validate company URLs
        valid_urls = [url for url in request.company_urls if url and 'linkedin.com/company/' in url]
        
        if not valid_urls:
            return {
                "success": False,
                "message": "No valid LinkedIn company URLs provided"
            }
        
        # Add the background task
        background_tasks.add_task(
            crawl_company_details_background,
            request.email,
            request.password,
            valid_urls
        )
        
        # Initialize cache entries for these URLs if they don't exist
        for url in valid_urls:
            if url not in company_details_cache:
                company_details_cache[url] = {
                    'basic_info': None,
                    'detailed_info': None,
                    'search_id': 'manual',
                    'status': 'pending'
                }
        
        return {
            "success": True,
            "message": f"Started background crawling of {len(valid_urls)} company URLs",
            "company_urls": valid_urls
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company-details/{search_id}")
async def get_company_details(search_id: str):
    """Get all company details for a specific search ID"""
    try:
        # Filter companies by search ID
        search_companies = {
            url: details for url, details in company_details_cache.items()
            if details.get('search_id') == search_id
        }
        
        if not search_companies:
            return {
                "success": False,
                "message": f"No companies found for search ID: {search_id}"
            }
        
        # Count companies by status
        status_counts = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0
        }
        
        for company_url, details in search_companies.items():
            status = details.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
        
        # Prepare the response data
        companies_data = []
        for company_url, details in search_companies.items():
            company_data = {
                'url': company_url,
                'status': details.get('status', 'unknown')
            }
            
            # Include basic info if available
            if details.get('basic_info'):
                company_data.update(details['basic_info'])
            
            # Include detailed info if available
            if details.get('detailed_info'):
                # If there's overlap between basic and detailed info, detailed takes precedence
                company_data.update(details['detailed_info'])
            
            # Add error if present
            if details.get('error'):
                company_data['error'] = details['error']
                
            companies_data.append(company_data)
        
        return {
            "success": True,
            "message": f"Found {len(search_companies)} companies for search ID: {search_id}",
            "status_summary": status_counts,
            "data": companies_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company-details-url")
async def get_company_details_by_url(url: str):
    """Get company details for a specific URL"""
    try:
        if url not in company_details_cache:
            return {
                "success": False,
                "message": f"No company details found for URL: {url}"
            }
        
        details = company_details_cache[url]
        
        # Prepare the response data
        company_data = {
            'url': url,
            'status': details.get('status', 'unknown')
        }
        
        # Include basic info if available
        if details.get('basic_info'):
            company_data.update(details['basic_info'])
        
        # Include detailed info if available
        if details.get('detailed_info'):
            # If there's overlap between basic and detailed info, detailed takes precedence
            company_data.update(details['detailed_info'])
        
        # Add error if present
        if details.get('error'):
            company_data['error'] = details['error']
        
        return {
            "success": True,
            "message": f"Found company details for URL: {url}",
            "data": company_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CrawlSearchRequest(BaseModel):
    search_id: str
    email: str
    password: str

@router.post("/crawl-search-jobs")
async def crawl_search_jobs(request: CrawlSearchRequest, background_tasks: BackgroundTasks):
    """Start background crawling of all job details from a previous search"""
    try:
        # Filter jobs by search ID
        search_jobs = {
            url: details for url, details in job_details_cache.items()
            if details.get('search_id') == request.search_id
        }
        
        if not search_jobs:
            return {
                "success": False,
                "message": f"No jobs found for search ID: {request.search_id}"
            }
        
        # Get job URLs that need crawling (don't have detailed info yet)
        urls_to_crawl = []
        for url, details in search_jobs.items():
            if details.get('status') == 'pending' or details.get('detailed_info') is None:
                urls_to_crawl.append(url)
        
        if not urls_to_crawl:
            return {
                "success": False,
                "message": f"All jobs for search ID {request.search_id} already have detailed information"
            }
        
        # Add the background task
        background_tasks.add_task(
            crawl_job_details_background,
            request.email,
            request.password,
            urls_to_crawl
        )
        
        return {
            "success": True,
            "message": f"Started background crawling of {len(urls_to_crawl)} job URLs from search ID: {request.search_id}",
            "job_urls": urls_to_crawl
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
