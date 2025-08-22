import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Optional
import json
import time
from datetime import datetime

class LinkedInScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        
    async def start_browser(self, headless: bool = False, slow_mo: int = 1000):
        """Start the browser instance with visual feedback"""
        print("🚀 Starting browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with visual settings
        self.browser = await self.playwright.chromium.launch(
            headless=headless,  # Set to False to see the browser
            slow_mo=slow_mo,    # Slow down actions to see what's happening
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        
        # Add stealth scripts to avoid detection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("✅ Browser started successfully!")
        
    async def login(self, email: str, password: str, wait_for_manual: bool = False):
        """Login to LinkedIn with visual feedback and manual intervention support"""
        try:
            print("🔐 Starting LinkedIn login process...")
            await self.page.goto('https://www.linkedin.com')
            await self.page.wait_for_load_state('networkidle')
            
            print("📧 Filling email...")
            await self.page.fill('#username', email)
            await asyncio.sleep(1)
            
            print("🔑 Filling password...")
            await self.page.fill('#password', password)
            await asyncio.sleep(1)
            
            print("🖱️ Clicking sign in button...")
            await self.page.click('button[type="submit"]')
            
            # Wait for potential redirects or challenges
            await asyncio.sleep(3)
            
            # Check if we need manual intervention (2FA, captcha, etc.)
            current_url = self.page.url
            
            if "checkpoint" in current_url or "challenge" in current_url:
                print("⚠️  Login challenge detected! Please complete manually in the browser.")
                print("⏳ Waiting for manual completion...")
                
                if wait_for_manual:
                    # Wait for user to manually complete the challenge
                    await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=300000)  # 5 minutes
                else:
                    # Wait a bit and check if challenge was resolved
                    await asyncio.sleep(10)
            
            # Check if login was successful
            try:
                await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=15000)
                print("✅ Successfully logged in to LinkedIn!")
                return True
            except:
                # Check if we're on the feed page
                if "feed" in self.page.url or "mynetwork" in self.page.url:
                    print("✅ Successfully logged in to LinkedIn!")
                    return True
                else:
                    print("❌ Login may have failed. Current URL:", self.page.url)
                    return False
                    
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def manual_login(self, email: str, password: str):
        """Login with manual intervention for complex scenarios"""
        try:
            print("🔐 Starting manual login process...")
            await self.page.goto('https://www.linkedin.com/login')
            await self.page.wait_for_load_state('networkidle')
            
            print("📧 Filling email...")
            await self.page.fill('#username', email)
            await asyncio.sleep(1)
            
            print("🔑 Filling password...")
            await self.page.fill('#password', password)
            await asyncio.sleep(1)
            
            print("🖱️ Clicking sign in button...")
            await self.page.click('button[type="submit"]')
            
            print("⏳ Waiting for manual completion of any challenges...")
            print("💡 Please complete any 2FA, captcha, or other challenges in the browser window.")
            print("⏰ You have 5 minutes to complete the login...")
            
            # Wait for manual completion
            await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=300000)  # 5 minutes
            
            print("✅ Manual login completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Manual login error: {str(e)}")
            return False
    
    async def close(self):
        """Close the browser"""
        print(" Closing browser...")
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ Browser closed successfully!")

    async def search_jobs_from_feed(self, email: str, password: str, job_title: str, max_jobs: int = 10):
        """Search jobs from LinkedIn feed page using the main search box"""
        try:
            print(f"🚀 Starting job search from feed for: {job_title}")
            
            # Step 1: Login to LinkedIn
            print("🔐 Step 1: Logging into LinkedIn...")
            await self.page.goto('https://www.linkedin.com/login')
            await asyncio.sleep(2)
            
            # Fill email and password
            await self.page.fill('#username', email)
            await asyncio.sleep(1)
            await self.page.fill('#password', password)
            await asyncio.sleep(1)
            
            # Click sign in
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(3)
            
            # Wait for login to complete and redirect to feed
            try:
                await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=15000)
                print("✅ Login successful! Redirected to feed page.")
            except:
                print("⚠️ Login may need manual intervention, continuing...")
                await asyncio.sleep(5)
            
            # Step 2: Find and use the main search box on feed page immediately
            print(" Step 2: Using main search box on feed page...")
            try:
                # Try different selectors for the main search box on feed page
                search_box_selectors = [
                    'input[aria-label="Search"]',
                    'input[placeholder*="Search"]',
                    'input[type="text"]',
                    '.search-global-typeahead__input',
                    'input[name="keywords"]',
                    'input[data-control-name="nav.searchbox"]'
                ]
                
                search_box = None
                for selector in search_box_selectors:
                    try:
                        search_box = await self.page.wait_for_selector(selector, timeout=3000)
                        if search_box:
                            print(f"✅ Found search box with selector: {selector}")
                            break
                    except:
                        continue
                
                if search_box:
                    # Click on search box and fill job title
                    await search_box.click()
                    await search_box.fill('')  # Clear existing text
                    await asyncio.sleep(1)
                    await search_box.fill(job_title)
                    print(f"✅ Job title filled in search box: {job_title}")
                    
                    # Press Enter to search
                    await self.page.keyboard.press('Enter')
                    print("✅ Pressed Enter to search")
                    
                else:
                    print("❌ Could not find search box on feed page")
                    return []
                    
            except Exception as e:
                print(f"❌ Error using search box: {str(e)}")
                return []
            
            # Step 3: Wait briefly for search results
            print("⏳ Step 3: Waiting for search results...")
            await asyncio.sleep(3)
            
            # Step 4: Check if we're on jobs page, if not navigate to jobs
            current_url = self.page.url
            if "jobs" not in current_url:
                print(" Step 4: Navigating to jobs section...")
                try:
                    # Try to click on jobs tab or navigate to jobs
                    jobs_selectors = [
                        'a[href*="/jobs/"]',
                        'a:has-text("Jobs")',
                        'button:has-text("Jobs")',
                        '[data-control-name="nav.jobs"]'
                    ]
                    
                    jobs_clicked = False
                    for selector in jobs_selectors:
                        try:
                            jobs_link = await self.page.wait_for_selector(selector, timeout=3000)
                            if jobs_link:
                                await jobs_link.click()
                                print("✅ Clicked on Jobs tab")
                                jobs_clicked = True
                                break
                        except:
                            continue
                    
                    if not jobs_clicked:
                        # Navigate directly to jobs page
                        await self.page.goto('https://www.linkedin.com/jobs')
                        print("✅ Navigated directly to jobs page")
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Error navigating to jobs: {str(e)}")
                    return []
            
            # Step 5: Scroll to load more jobs
            print("📜 Step 5: Scrolling to load more jobs...")
            for i in range(3):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            
            # Step 6: Extract job listings
            print(" Step 6: Extracting job data...")
            jobs = []
            
            # Try different selectors for job cards
            job_card_selectors = [
                '.job-search-card',
                '.job-card-container',
                '.job-card',
                '[data-job-id]',
                '.jobs-search-results__list-item',
                '.job-card-list__item',
                '.job-search-results__list-item'
            ]
            
            job_cards = []
            for selector in job_card_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    job_cards = await self.page.query_selector_all(selector)
                    if job_cards:
                        print(f"✅ Found {len(job_cards)} job cards using selector: {selector}")
                        break
                except:
                    continue
            
            if not job_cards:
                print("❌ No job cards found")
                return []
            
            # Extract data from each job card
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    # Extract job title
                    title_selectors = [
                        '.job-search-card__title',
                        '.job-card-list__title',
                        'h3',
                        '.job-title',
                        'a[href*="/jobs/view/"]',
                        '.job-card-container__title'
                    ]
                    
                    title = "N/A"
                    for selector in title_selectors:
                        try:
                            title_element = await card.query_selector(selector)
                            if title_element:
                                title = await title_element.inner_text()
                                break
                        except:
                            continue
                    
                    # Extract company name
                    company_selectors = [
                        '.job-search-card__subtitle',
                        '.job-card-container__company-name',
                        '.job-card-container__subtitle',
                        '.company-name',
                        '.job-card-container__company'
                    ]
                    
                    company = "N/A"
                    for selector in company_selectors:
                        try:
                            company_element = await card.query_selector(selector)
                            if company_element:
                                company = await company_element.inner_text()
                                break
                        except:
                            continue
                    
                    # Extract location
                    location_selectors = [
                        '.job-search-card__location',
                        '.job-card-container__location',
                        '.job-location',
                        '.job-card-container__location-text'
                    ]
                    
                    job_location = "N/A"
                    for selector in location_selectors:
                        try:
                            location_element = await card.query_selector(selector)
                            if location_element:
                                job_location = await location_element.inner_text()
                                break
                        except:
                            continue
                    
                    # Extract job URL
                    link_element = await card.query_selector('a[href*="/jobs/view/"]')
                    job_url = None
                    if link_element:
                        job_url = await link_element.get_attribute('href')
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://www.linkedin.com{job_url}"
                    
                    # Extract posted time
                    time_selectors = [
                        '.job-search-card__listdate',
                        '.job-card-container__listdate',
                        '.job-posted-time',
                        '.job-card-container__time'
                    ]
                    
                    posted_time = "N/A"
                    for selector in time_selectors:
                        try:
                            time_element = await card.query_selector(selector)
                            if time_element:
                                posted_time = await time_element.inner_text()
                                break
                        except:
                            continue
                    
                    job_data = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": job_location.strip(),
                        "url": job_url,
                        "posted_time": posted_time.strip(),
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    jobs.append(job_data)
                    print(f"✅ Extracted job {i+1}: {title}")
                    
                except Exception as e:
                    print(f"⚠️ Error extracting job {i+1}: {str(e)}")
                    continue
            
            print(f" Successfully scraped {len(jobs)} jobs!")
            return jobs
            
        except Exception as e:
            print(f"❌ Search jobs from feed error: {str(e)}")
            return []