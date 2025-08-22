from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import login, scraper
# Create the FastAPI app
app = FastAPI(
    title="Hackathon Web Scraper API",
    description="A powerful web scraping API with authentication and filtering capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return {"message": "Hackathon Scraper API is running 🚀"}

# Include the routers
app.include_router(login.router, prefix="/api")
app.include_router(scraper.router, prefix="/api")
