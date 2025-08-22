import asyncio
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, Page
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def scrape_website(
        self, 
        url: str, 
        username: str, 
        password: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scrape a website with authentication and optional filters
        
        Args:
            url: Website URL to scrape
            username: Login username
            password: Login password
            filters: Optional filters for data extraction
            
        Returns:
            Dictionary containing scraped data and metadata
        """
        try:
            # Navigate to the website
            await self.page.goto(url, wait_until="networkidle")
            
            # Handle login if credentials provided
            if username and password:
                await self._handle_login(username, password)
            
            # Apply filters if provided
            if filters:
                await self._apply_filters(filters)
            
            # Extract data based on common patterns
            scraped_data = await self._extract_data(filters)
            
            return {
                "success": True,
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "data": scraped_data,
                "metadata": {
                    "page_title": await self.page.title(),
                    "url": self.page.url,
                    "filters_applied": filters or {}
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_login(self, username: str, password: str):
        """Handle website login"""
        try:
            # Common login form selectors
            username_selectors = [
                'input[name="username"]',
                'input[name="email"]',
                'input[name="user"]',
                'input[type="email"]',
                'input[id*="username"]',
                'input[id*="email"]'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[id*="password"]'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'form button'
            ]
            
            # Try to fill username
            for selector in username_selectors:
                try:
                    await self.page.fill(selector, username)
                    break
                except:
                    continue
            
            # Try to fill password
            for selector in password_selectors:
                try:
                    await self.page.fill(selector, password)
                    break
                except:
                    continue
            
            # Try to submit
            for selector in submit_selectors:
                try:
                    await self.page.click(selector)
                    await self.page.wait_for_load_state("networkidle")
                    break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Login handling failed: {str(e)}")
    
    async def _apply_filters(self, filters: Dict[str, Any]):
        """Apply filters to the page"""
        try:
            # Handle search filters
            if "search" in filters:
                search_selectors = [
                    'input[name="search"]',
                    'input[type="search"]',
                    'input[placeholder*="search"]',
                    'input[id*="search"]'
                ]
                
                for selector in search_selectors:
                    try:
                        await self.page.fill(selector, filters["search"])
                        await self.page.press(selector, "Enter")
                        await self.page.wait_for_load_state("networkidle")
                        break
                    except:
                        continue
            
            # Handle category filters
            if "category" in filters:
                category_selectors = [
                    f'a:has-text("{filters["category"]}")',
                    f'button:has-text("{filters["category"]}")',
                    f'select option:has-text("{filters["category"]}")'
                ]
                
                for selector in category_selectors:
                    try:
                        await self.page.click(selector)
                        await self.page.wait_for_load_state("networkidle")
                        break
                    except:
                        continue
                        
        except Exception as e:
            logger.warning(f"Filter application failed: {str(e)}")
    
    async def _extract_data(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract data from the page"""
        try:
            data = {
                "title": await self.page.title(),
                "url": self.page.url,
                "text_content": await self._extract_text_content(),
                "links": await self._extract_links(),
                "images": await self._extract_images(),
                "tables": await self._extract_tables(),
                "forms": await self._extract_forms()
            }
            
            # Apply specific data filters if provided
            if filters and "data_types" in filters:
                filtered_data = {}
                for data_type in filters["data_types"]:
                    if data_type in data:
                        filtered_data[data_type] = data[data_type]
                data = filtered_data
            
            return data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            return {"error": str(e)}
    
    async def _extract_text_content(self) -> List[Dict[str, str]]:
        """Extract text content from the page"""
        try:
            # Extract headings
            headings = await self.page.query_selector_all("h1, h2, h3, h4, h5, h6")
            heading_data = []
            for heading in headings:
                text = await heading.text_content()
                tag_name = await heading.evaluate("el => el.tagName.toLowerCase()")
                heading_data.append({
                    "type": "heading",
                    "level": tag_name,
                    "text": text.strip() if text else ""
                })
            
            # Extract paragraphs
            paragraphs = await self.page.query_selector_all("p")
            paragraph_data = []
            for p in paragraphs:
                text = await p.text_content()
                if text and text.strip():
                    paragraph_data.append({
                        "type": "paragraph",
                        "text": text.strip()
                    })
            
            return heading_data + paragraph_data
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            return []
    
    async def _extract_links(self) -> List[Dict[str, str]]:
        """Extract links from the page"""
        try:
            links = await self.page.query_selector_all("a")
            link_data = []
            for link in links:
                href = await link.get_attribute("href")
                text = await link.text_content()
                if href:
                    link_data.append({
                        "url": href,
                        "text": text.strip() if text else "",
                        "title": await link.get_attribute("title") or ""
                    })
            return link_data
            
        except Exception as e:
            logger.error(f"Link extraction failed: {str(e)}")
            return []
    
    async def _extract_images(self) -> List[Dict[str, str]]:
        """Extract images from the page"""
        try:
            images = await self.page.query_selector_all("img")
            image_data = []
            for img in images:
                src = await img.get_attribute("src")
                alt = await img.get_attribute("alt")
                if src:
                    image_data.append({
                        "src": src,
                        "alt": alt or "",
                        "title": await img.get_attribute("title") or ""
                    })
            return image_data
            
        except Exception as e:
            logger.error(f"Image extraction failed: {str(e)}")
            return []
    
    async def _extract_tables(self) -> List[Dict[str, Any]]:
        """Extract table data from the page"""
        try:
            tables = await self.page.query_selector_all("table")
            table_data = []
            for table in tables:
                rows = await table.query_selector_all("tr")
                table_rows = []
                for row in rows:
                    cells = await row.query_selector_all("td, th")
                    row_data = []
                    for cell in cells:
                        text = await cell.text_content()
                        row_data.append(text.strip() if text else "")
                    if row_data:
                        table_rows.append(row_data)
                
                if table_rows:
                    table_data.append({
                        "rows": table_rows,
                        "headers": table_rows[0] if table_rows else []
                    })
            return table_data
            
        except Exception as e:
            logger.error(f"Table extraction failed: {str(e)}")
            return []
    
    async def _extract_forms(self) -> List[Dict[str, Any]]:
        """Extract form data from the page"""
        try:
            forms = await self.page.query_selector_all("form")
            form_data = []
            for form in forms:
                inputs = await form.query_selector_all("input, select, textarea")
                form_fields = []
                for input_elem in inputs:
                    input_type = await input_elem.get_attribute("type") or "text"
                    input_name = await input_elem.get_attribute("name") or ""
                    input_id = await input_elem.get_attribute("id") or ""
                    
                    form_fields.append({
                        "type": input_type,
                        "name": input_name,
                        "id": input_id,
                        "placeholder": await input_elem.get_attribute("placeholder") or ""
                    })
                
                form_data.append({
                    "action": await form.get_attribute("action") or "",
                    "method": await form.get_attribute("method") or "get",
                    "fields": form_fields
                })
            return form_data
            
        except Exception as e:
            logger.error(f"Form extraction failed: {str(e)}")
            return []

# Global scraper instance
scraper_service = WebScraper()

