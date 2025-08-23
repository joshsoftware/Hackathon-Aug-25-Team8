from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import login, linkedin
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hackathon Scraper API is running 🚀"}


app.include_router(login.router, prefix="/api")
app.include_router(linkedin.router, prefix="/api")