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
            
    async def scrape_job_details(self, job_url: str):
        """Scrape detailed job information from a specific job page URL"""
        try:
            print(f"🔍 Scraping detailed job information from: {job_url}")
            
            # Navigate to the job page
            await self.page.goto(job_url, timeout=60000)
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # Check if we're on a search page with job details panel or a dedicated job page
            is_search_page = False
            try:
                # Check for job cards list which indicates we're on a search page
                job_cards_list = await self.page.query_selector('.jobs-search-results-list')
                job_details_panel = await self.page.query_selector('.jobs-search-two-pane__details')
                
                if job_cards_list and job_details_panel:
                    is_search_page = True
                    print("✅ Detected search page with job details panel")
            except:
                pass
            
            # Extract job details
            job_details = {}
            
            # Extract job title
            title_selectors = [
                'h1.job-title',
                'h1.topcard__title',
                'h1',
                '.job-details-jobs-unified-top-card__job-title',
                '.jobs-unified-top-card__job-title',
                '.jobs-search-results-list__text-title',
                '.jobs-details-top-card__job-title',
                '.jobs-details__main-title'
            ]
            
            for selector in title_selectors:
                try:
                    title_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if title_element:
                        job_details['title'] = await title_element.inner_text()
                        break
                except:
                    continue
                    
            if 'title' not in job_details:
                job_details['title'] = "N/A"
            
            # Extract company name
            company_selectors = [
                '.topcard__org-name-link',
                '.jobs-unified-top-card__company-name',
                '.job-details-jobs-unified-top-card__company-name',
                'a.topcard__org-name-link',
                '.jobs-unified-top-card__subtitle-primary-grouping a',
                '.jobs-details-top-card__company-url',
                '.jobs-details-top-card__company-info',
                '.jobs-search-results-list__text-subtitle'
            ]
            
            for selector in company_selectors:
                try:
                    company_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if company_element:
                        job_details['company'] = await company_element.inner_text()
                        break
                except:
                    continue
                    
            if 'company' not in job_details:
                job_details['company'] = "N/A"
            
            # Extract location
            location_selectors = [
                '.topcard__flavor--bullet',
                '.jobs-unified-top-card__bullet',
                '.job-details-jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__subtitle-primary-grouping .jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__location',
                '.jobs-details-top-card__bullet',
                '.jobs-details-top-card__location',
                '.jobs-search-results-list__text-location'
            ]
            
            for selector in location_selectors:
                try:
                    location_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if location_element:
                        job_details['location'] = await location_element.inner_text()
                        break
                except:
                    continue
                    
            if 'location' not in job_details:
                job_details['location'] = "N/A"
            
            # Extract job description
            description_selectors = [
                '.description__text',
                '.show-more-less-html__markup',
                '.jobs-description-content',
                '.jobs-description__content',
                '.job-details-jobs-unified-description__content',
                '.jobs-box__html-content',
                '.jobs-description',
                '.jobs-details__description-container',
                '#job-details'
            ]
            
            for selector in description_selectors:
                try:
                    description_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if description_element:
                        job_details['description'] = await description_element.inner_text()
                        break
                except:
                    continue
                    
            if 'description' not in job_details:
                job_details['description'] = "N/A"
            
            # Extract job criteria/requirements
            criteria_selectors = [
                '.description__job-criteria-list',
                '.job-criteria-list',
                '.jobs-unified-description__job-criteria-list',
                '.job-details-jobs-unified-description__job-criteria-list',
                '.jobs-description-details__list',
                '.jobs-details__job-criteria-list',
                '.jobs-box__list'
            ]
            
            job_details['criteria'] = {}
            
            for selector in criteria_selectors:
                try:
                    criteria_elements = await self.page.query_selector_all(f"{selector} > li")
                    if criteria_elements:
                        for element in criteria_elements:
                            try:
                                label_element = await element.query_selector('.job-criteria-subheader')
                                value_element = await element.query_selector('.job-criteria-text')
                                
                                if label_element and value_element:
                                    label = await label_element.inner_text()
                                    value = await value_element.inner_text()
                                    job_details['criteria'][label.strip()] = value.strip()
                            except:
                                continue
                        break
                except:
                    continue
            
            # Extract application details
            application_selectors = [
                '.jobs-apply-button',
                '.jobs-s-apply',
                '.jobs-unified-top-card__apply-button',
                '.job-details-jobs-unified-top-card__apply-button',
                '.jobs-details-top-card__apply-button',
                '.jobs-apply-button--top-card',
                'button:has-text("Easy Apply")',
                'button:has-text("Apply")'
            ]
            
            job_details['application_type'] = "Unknown"
            
            for selector in application_selectors:
                try:
                    apply_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if apply_button:
                        button_text = await apply_button.inner_text()
                        if "Apply" in button_text:
                            if "Easy Apply" in button_text:
                                job_details['application_type'] = "LinkedIn Easy Apply"
                            else:
                                job_details['application_type'] = "Apply on LinkedIn"
                        break
                except:
                    continue
            
            # Extract posted date
            date_selectors = [
                '.posted-time-ago__text',
                '.job-posted-time',
                '.jobs-unified-top-card__posted-date',
                '.job-details-jobs-unified-top-card__posted-date',
                '.jobs-details-top-card__posted-date',
                '.jobs-details-top-card__job-info time',
                '.job-search-card__listdate',
                'time'
            ]
            
            for selector in date_selectors:
                try:
                    date_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if date_element:
                        job_details['posted_date'] = await date_element.inner_text()
                        break
                except:
                    continue
                    
            if 'posted_date' not in job_details:
                job_details['posted_date'] = "N/A"
            
            # Extract number of applicants
            applicants_selectors = [
                '.num-applicants',
                '.jobs-unified-top-card__applicant-count',
                '.job-details-jobs-unified-top-card__applicant-count',
                '.jobs-details-top-card__applicant-count',
                '.jobs-details__applicant-count',
                'span:has-text("applicants")',
                'span:has-text("Over")'
            ]
            
            for selector in applicants_selectors:
                try:
                    applicants_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if applicants_element:
                        job_details['applicants'] = await applicants_element.inner_text()
                        break
                except:
                    continue
                    
            if 'applicants' not in job_details:
                job_details['applicants'] = "N/A"
            
            # Extract company details if available
            company_details_selectors = [
                '.jobs-company',
                '.jobs-unified-top-card__company-info',
                '.job-details-jobs-unified-top-card__company-info',
                '.jobs-details-top-card__company-info',
                '.jobs-company__box',
                '.jobs-company-details'
            ]
            
            job_details['company_details'] = {}
            
            for selector in company_details_selectors:
                try:
                    company_size_element = await self.page.wait_for_selector(f"{selector} .company-size", timeout=3000)
                    if company_size_element:
                        job_details['company_details']['size'] = await company_size_element.inner_text()
                except:
                    pass
                
                try:
                    company_industry_element = await self.page.wait_for_selector(f"{selector} .company-industry", timeout=3000)
                    if company_industry_element:
                        job_details['company_details']['industry'] = await company_industry_element.inner_text()
                except:
                    pass
            
            # Extract hiring team information if available
            try:
                hiring_team_section = await self.page.query_selector('.jobs-details__meet-the-team-section')
                if hiring_team_section:
                    job_details['hiring_team'] = []
                    team_members = await hiring_team_section.query_selector_all('li')
                    for member in team_members:
                        try:
                            name_element = await member.query_selector('.artdeco-entity-lockup__title')
                            role_element = await member.query_selector('.artdeco-entity-lockup__subtitle')
                            
                            if name_element and role_element:
                                name = await name_element.inner_text()
                                role = await role_element.inner_text()
                                job_details['hiring_team'].append({
                                    'name': name.strip(),
                                    'role': role.strip()
                                })
                        except:
                            continue
            except:
                pass
                
            # Extract skills match information if available
            try:
                skills_match_element = await self.page.query_selector('span:has-text("skills match")')
                if skills_match_element:
                    skills_text = await skills_match_element.inner_text()
                    job_details['skills_match'] = skills_text.strip()
            except:
                pass
                
            # Extract job type (remote, hybrid, on-site)
            try:
                job_type_elements = await self.page.query_selector_all('.jobs-details-top-card__workplace-type')
                if job_type_elements:
                    for element in job_type_elements:
                        job_type_text = await element.inner_text()
                        if 'Remote' in job_type_text:
                            job_details['workplace_type'] = 'Remote'
                        elif 'Hybrid' in job_type_text:
                            job_details['workplace_type'] = 'Hybrid'
                        elif 'On-site' in job_type_text:
                            job_details['workplace_type'] = 'On-site'
            except:
                pass
                
            # Extract education requirements
            try:
                education_section = await self.page.query_selector('h3:has-text("Education")')
                if education_section:
                    parent_section = await education_section.evaluate('node => node.parentElement')
                    if parent_section:
                        education_text = await self.page.evaluate('node => node.textContent', parent_section)
                        job_details['education_requirements'] = education_text.replace('Education:', '').strip()
            except:
                pass
                
            # Extract experience requirements
            try:
                experience_section = await self.page.query_selector('h3:has-text("Experience")')
                if experience_section:
                    parent_section = await experience_section.evaluate('node => node.parentElement')
                    if parent_section:
                        experience_text = await self.page.evaluate('node => node.textContent', parent_section)
                        job_details['experience_requirements'] = experience_text.replace('Experience:', '').strip()
            except:
                pass
            
            # Add metadata
            job_details['url'] = job_url
            job_details['scraped_at'] = datetime.now().isoformat()
            job_details['is_search_page_view'] = is_search_page
            
            print(f"✅ Successfully scraped detailed job information: {job_details.get('title', 'Unknown Title')}")
            return job_details
            
        except Exception as e:
            print(f"❌ Error scraping job details from {job_url}: {str(e)}")
            return {
                "url": job_url,
                "error": str(e),
                "scraped_at": datetime.now().isoformat()
            }

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

    async def search_jobs_direct_url(self, email: str, password: str, job_title: str, max_jobs: int = 10):
        """Search jobs by going directly to LinkedIn jobs search URL and scraping all data"""
        try:
            print(f"🚀 Starting direct job search for: {job_title}")
            
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
            
            # Wait for login to complete
            try:
                await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=15000)
                print("✅ Login successful!")
            except:
                print("⚠️ Login may need manual intervention, continuing...")
                await asyncio.sleep(5)
            
            # Step 2: Go directly to LinkedIn jobs search page
            print(" Step 2: Going directly to LinkedIn jobs search page...")
            await self.page.goto('https://www.linkedin.com/jobs/search')
            await asyncio.sleep(3)
            
            # Step 3: Fill job title in the search box
            print("📝 Step 3: Filling job title in search box...")
            job_title_selectors = [
                'input[aria-label*="Search by title"]',
                'input[aria-label*="Search by title, skill, or company"]',
                'input[placeholder*="Search by title"]',
                'input[name="keywords"]',
                '.jobs-search-box__text-input[aria-label*="Search by title"]',
                'input[type="text"]',
                'input[placeholder*="Search jobs"]'
            ]
            
            job_title_input = None
            for selector in job_title_selectors:
                try:
                    job_title_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if job_title_input:
                        print(f"✅ Found job title input with selector: {selector}")
                        break
                except:
                    continue
            
            if job_title_input:
                await job_title_input.click()
                await job_title_input.fill('')  # Clear existing text
                await asyncio.sleep(1)
                await job_title_input.fill(job_title)
                print(f"✅ Job title filled: {job_title}")
                await asyncio.sleep(1)
            else:
                print("❌ Could not find job title input")
                return []
            
            # Step 4: Click search button or press Enter
            print(" Step 4: Triggering search...")
            search_button_selectors = [
                'button:has-text("Search now")',
                'button[aria-label="Search"]',
                'button[type="submit"]',
                '.jobs-search-box__submit-button',
                'button:has-text("Search")',
                'button:has-text("Search jobs")',
                'input[type="submit"]',
                '.search-button',
                'button.search-button'
            ]
            
            search_clicked = False
            for selector in search_button_selectors:
                try:
                    search_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if search_button:
                        await search_button.click()
                        print(f"✅ Clicked search button with selector: {selector}")
                        search_clicked = True
                        break
                except:
                    continue
            
            # If no search button found, try pressing Enter
            if not search_clicked:
                print("⚠️ No search button found, trying Enter key...")
                try:
                    await self.page.keyboard.press('Enter')
                    print("✅ Pressed Enter key for search")
                    search_clicked = True
                except Exception as e:
                    print(f"❌ Error pressing Enter: {str(e)}")
            
            if not search_clicked:
                print("❌ Could not trigger search")
                return []
            
            # Step 5: Wait for search results to load
            print("⏳ Step 5: Waiting for search results...")
            await asyncio.sleep(5)
            
            # Step 6: Scroll to load more jobs
            print("📜 Step 6: Scrolling to load more jobs...")
            for i in range(5):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # Step 7: Extract all job data from the current page
            print(" Step 7: Extracting all job data from the page...")
            jobs = []
            
            # Try different selectors for job cards
            job_card_selectors = [
                '.job-search-card',
                '.job-card-container',
                '.job-card',
                '[data-job-id]',
                '.jobs-search-results__list-item',
                '.job-card-list__item',
                '.job-search-results__list-item',
                'li[data-job-id]',
                '.job-card-list__item'
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
                        '.job-card-container__title',
                        'h2',
                        'h4'
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
                        '.job-card-container__company',
                        '.job-company-name'
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
                        '.job-card-container__location-text',
                        '.job-location-text'
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
                    
                    # If we couldn't extract company or location from the card, try clicking on it and getting from the details panel
                    if company == "N/A" or job_location == "N/A":
                        try:
                            # Click on the job card to show details
                            await card.click()
                            await asyncio.sleep(2)  # Wait for details to load
                            
                            # Try to extract company from details panel
                            if company == "N/A":
                                company_detail_selectors = [
                                    '.jobs-unified-top-card__company-name',
                                    '.jobs-details-top-card__company-url',
                                    '.jobs-details-top-card__company-info'
                                ]
                                
                                for selector in company_detail_selectors:
                                    try:
                                        company_element = await self.page.wait_for_selector(selector, timeout=2000)
                                        if company_element:
                                            company = await company_element.inner_text()
                                            break
                                    except:
                                        continue
                            
                            # Try to extract location from details panel
                            if job_location == "N/A":
                                location_detail_selectors = [
                                    '.jobs-unified-top-card__bullet',
                                    '.jobs-unified-top-card__location',
                                    '.jobs-details-top-card__bullet',
                                    '.jobs-details-top-card__location'
                                ]
                                
                                for selector in location_detail_selectors:
                                    try:
                                        location_element = await self.page.wait_for_selector(selector, timeout=2000)
                                        if location_element:
                                            job_location = await location_element.inner_text()
                                            break
                                    except:
                                        continue
                        except Exception as e:
                            print(f"⚠️ Error getting details from panel: {str(e)}")
                    
                    # Extract job URL
                    link_selectors = [
                        'a[href*="/jobs/search"]',
                        'a[href*="/jobs/view/"]',
                        'a[href*="linkedin.com/jobs"]',
                        'a[data-job-id]',
                        'a'
                    ]
                    
                    job_url = None
                    for selector in link_selectors:
                        try:
                            link_element = await card.query_selector(selector)
                            if link_element:
                                href = await link_element.get_attribute('href')
                                if href and ('/jobs/search' in href or '/jobs/view/' in href):
                                    if not href.startswith('http'):
                                        href = f"https://www.linkedin.com{href}"
                                    job_url = href
                                    break
                        except:
                            continue
                    
                    # Extract posted time
                    time_selectors = [
                        '.job-search-card__listdate',
                        '.job-card-container__listdate',
                        '.job-posted-time',
                        '.job-card-container__time',
                        '.job-time'
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
                    
                    # Extract job type/level
                    type_selectors = [
                        '.job-search-card__metadata-item',
                        '.job-card-container__metadata-item',
                        '.job-type',
                        '.job-level',
                        '.job-seniority'
                    ]
                    
                    job_type = "N/A"
                    for selector in type_selectors:
                        try:
                            type_element = await card.query_selector(selector)
                            if type_element:
                                job_type = await type_element.inner_text()
                                break
                        except:
                            continue
                    
                    # Extract salary if available
                    salary_selectors = [
                        '.job-search-card__salary',
                        '.job-card-container__salary',
                        '.job-salary',
                        '.salary'
                    ]
                    
                    salary = "N/A"
                    for selector in salary_selectors:
                        try:
                            salary_element = await card.query_selector(selector)
                            if salary_element:
                                salary = await salary_element.inner_text()
                                break
                        except:
                            continue
                    
                    # Create job data object
                    job_data = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": job_location.strip(),
                        "url": job_url,
                        "posted_time": posted_time.strip(),
                        "job_type": job_type.strip(),
                        "salary": salary.strip(),
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    jobs.append(job_data)
                    print(f"✅ Extracted job {i+1}: {title}")
                    
                except Exception as e:
                    print(f"⚠️ Error extracting job {i+1}: {str(e)}")
                    continue
            
            print(f" Successfully scraped {len(jobs)} jobs from the search page!")
            return jobs
            
        except Exception as e:
            print(f"❌ Direct URL job search error: {str(e)}")
            return []
