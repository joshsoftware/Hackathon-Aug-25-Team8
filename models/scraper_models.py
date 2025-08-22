from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class DataType(str, Enum):
    """Enum for data types that can be extracted"""
    TEXT_CONTENT = "text_content"
    LINKS = "links"
    IMAGES = "images"
    TABLES = "tables"
    FORMS = "forms"
    ALL = "all"

class ScrapeRequest(BaseModel):
    """Request model for scraping a website"""
    url: HttpUrl
    username: Optional[str] = None
    password: Optional[str] = None
    search_filter: Optional[str] = None
    category_filter: Optional[str] = None
    data_types: Optional[List[DataType]] = [DataType.ALL]
    
    @validator('data_types')
    def validate_data_types(cls, v):
        if v and DataType.ALL in v and len(v) > 1:
            raise ValueError("Cannot specify 'all' with other data types")
        return v

class ScrapeResponse(BaseModel):
    """Response model for scraping results"""
    success: bool
    url: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TextContentItem(BaseModel):
    """Model for text content items"""
    type: str
    text: str
    level: Optional[str] = None

class LinkItem(BaseModel):
    """Model for link items"""
    url: str
    text: str
    title: str

class ImageItem(BaseModel):
    """Model for image items"""
    src: str
    alt: str
    title: str

class TableItem(BaseModel):
    """Model for table items"""
    rows: List[List[str]]
    headers: List[str]

class FormField(BaseModel):
    """Model for form fields"""
    type: str
    name: str
    id: str
    placeholder: str

class FormItem(BaseModel):
    """Model for form items"""
    action: str
    method: str
    fields: List[FormField]

class ScrapedData(BaseModel):
    """Model for scraped data structure"""
    title: str
    url: str
    text_content: Optional[List[TextContentItem]] = None
    links: Optional[List[LinkItem]] = None
    images: Optional[List[ImageItem]] = None
    tables: Optional[List[TableItem]] = None
    forms: Optional[List[FormItem]] = None

class ScrapeMetadata(BaseModel):
    """Model for scraping metadata"""
    page_title: str
    url: str
    filters_applied: Dict[str, Any]

