import asyncio
import json
import time
from services.linkedin_scraper import LinkedInScraper

async def test_job_search_and_background_crawling():
    """
    Test the job search and background crawling functionality.
    This script demonstrates how to:
    1. Search for jobs
    2. Extract job links
    3. Crawl detailed job information in the background
    """
    try:
        print("🚀 Starting test of job search and background crawling")
        
        # Initialize the scraper
        scraper = LinkedInScraper()
        await scraper.start_browser(headless=False, slow_mo=1000)
        
        # Search parameters
        email = "your_email@example.com"  # Replace with your LinkedIn email
        password = "your_password"        # Replace with your LinkedIn password
        job_title = "Software Engineer"   # Example job title to search for
        max_jobs = 5                      # Limit to 5 jobs for testing
        
        # Step 1: Search for jobs
        print(f"📋 Step 1: Searching for '{job_title}' jobs")
        jobs = await scraper.search_jobs_direct_url(
            email=email,
            password=password,
            job_title=job_title,
            max_jobs=max_jobs
        )
        
        if not jobs:
            print("❌ No jobs found. Test failed.")
            await scraper.close()
            return
        
        print(f"✅ Found {len(jobs)} jobs")
        
        # Step 2: Extract job URLs
        job_urls = []
        for job in jobs:
            if job.get('url'):
                job_urls.append(job['url'])
                print(f"📌 Job: {job.get('title')} at {job.get('company')} - {job['url']}")
        
        if not job_urls:
            print("❌ No job URLs found. Test failed.")
            await scraper.close()
            return
        
        print(f"✅ Extracted {len(job_urls)} job URLs")
        
        # Step 3: Crawl detailed job information for the first job
        if job_urls:
            print(f"🔍 Step 3: Crawling detailed job information for the first job")
            first_job_url = job_urls[0]
            
            job_details = await scraper.scrape_job_details(first_job_url)
            
            print(f"✅ Successfully scraped detailed job information:")
            print(f"  Title: {job_details.get('title')}")
            print(f"  Company: {job_details.get('company')}")
            print(f"  Location: {job_details.get('location')}")
            print(f"  Description: {job_details.get('description')[:100]}...")  # Show first 100 chars
            
            # Save the detailed job information to a file
            with open('job_details.json', 'w') as f:
                json.dump(job_details, f, indent=2)
            print(f"✅ Saved detailed job information to job_details.json")
        
        # Step 4: Demonstrate background crawling (simulated)
        print(f"🔄 Step 4: Simulating background crawling for all job URLs")
        
        # In a real application, this would be handled by the API's background tasks
        # Here we'll just simulate it by processing one more job
        if len(job_urls) > 1:
            second_job_url = job_urls[1]
            print(f"🔍 Processing second job URL: {second_job_url}")
            
            # Simulate background processing
            print("⏳ Background task started...")
            job_details = await scraper.scrape_job_details(second_job_url)
            print("✅ Background task completed")
            
            print(f"✅ Successfully scraped detailed job information in background:")
            print(f"  Title: {job_details.get('title')}")
            print(f"  Company: {job_details.get('company')}")
            print(f"  Description: {job_details.get('description')[:100]}...")  # Show first 100 chars
        
        # Close the browser
        await scraper.close()
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_job_search_and_background_crawling())
