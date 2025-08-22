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