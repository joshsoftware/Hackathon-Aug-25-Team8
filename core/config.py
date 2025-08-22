import os
from typing import List, Union
from pydantic import validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Determine which environment to use
ENV = os.getenv("ENV", "production")

# Load the appropriate .env file
if ENV == "production":
    load_dotenv(".env.prod")
elif ENV == "staging":
    load_dotenv(".env.staging")
else:
    # Default to sample for development
    load_dotenv(".env.sample")

class Settings(BaseSettings):
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Hackathon Scraper API")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Playwright settings
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER: str = os.getenv("BROWSER", "chromium")
    
    class Config:
        case_sensitive = True

settings = Settings()
