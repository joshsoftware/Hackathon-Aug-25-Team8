from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

router = APIRouter()

@router.get("/login")
async def health_check():
    return {"message": "Login successful!"}