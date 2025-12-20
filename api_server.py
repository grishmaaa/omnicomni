"""
Enhanced FastAPI Backend with Database Integration
Connects Next.js frontend to PostgreSQL database and CommercialPipeline
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import your existing modules
from commercial.database import (
    get_connection, init_db, create_user, get_user_by_uid,
    save_video_metadata, get_user_videos, update_last_login
)
from commercial.subscription import (
    get_user_subscription, can_generate_video, increment_usage,
    create_subscription, SUBSCRIPTION_TIERS
)

app = FastAPI(title="AI Video Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://technov.ai",
        "https://www.technov.ai",
        "https://a4jtekyn.up.railway.app",  # Railway frontend URL
        "https://*.up.railway.app"  # Allow all Railway subdomains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (replace with Redis in production)
jobs = {}

# Request/Response Models
class GenerateRequest(BaseModel):
    topic: str
    style: str = "cinematic"
    aspect_ratio: str = "16:9"
    num_scenes: int = 5

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    plan: str = "free"

class VideoResponse(BaseModel):
    id: int
    topic: str
    file_path: str
    thumbnail_path: Optional[str]
    duration_seconds: int
    created_at: str

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

# Authentication endpoints
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login with Supabase Auth and database"""
    try:
        from commercial.auth_supabase import verify_password
        
        # Verify with Supabase Auth
        user_data = verify_password(request.email, request.password)
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get or create database user
        db_user = get_user_by_uid(user_data['uid'])
        if not db_user:
            db_user = create_user(
                firebase_uid=user_data['uid'],  # Column name stays same, but it's Supabase UID
                email=user_data['email'],
                display_name=user_data.get('display_name', '')
            )
        
        # Update last login
        update_last_login(user_data['uid'])
        
        # Get subscription
        subscription = get_user_subscription(db_user['id'])
        if not subscription:
            subscription = create_subscription(db_user['id'], 'free')
        
        return {
            "success": True,
            "session_token": user_data['uid'],  # Use UID as session token
            "user": {
                "id": db_user['id'],
                "uid": db_user['firebase_uid'],
                "email": db_user['email'],
                "name": db_user['display_name']
            },
            "subscription": {
                "tier": subscription['tier'],
                "status": subscription['status']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    """User registration with Supabase Auth"""
    try:
        from commercial.auth_supabase import signup_user
        
        # Create Supabase Auth user
        user_data = signup_user(
            email=request.email,
            password=request.password,
            display_name=request.name
        )
        
        # Create database user
        db_user = create_user(
            firebase_uid=user_data['uid'],  # Column name stays same, but it's Supabase UID
            email=user_data['email'],
            display_name=request.name
        )
        
        # Create subscription
        subscription = create_subscription(db_user['id'], request.plan)
        
        return {
            "success": True,
            "user": {
                "id": db_user['id'],
                "email": db_user['email'],
                "name": db_user['display_name']
            },
            "subscription": subscription,
            "message": "Account created successfully"
        }
        
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Video generation endpoints
@app.post("/api/generate")
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start video generation"""
    # TODO: Get user_id from session
    user_id = 1  # Mock for now
    
    try:
        # Get subscription
        subscription = get_user_subscription(user_id)
        tier = subscription['tier'] if subscription else 'free'
        
        # Check if user can generate
        can_generate, message = can_generate_video(user_id, tier)
        if not can_generate:
            raise HTTPException(status_code=403, detail=message)
        
        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "stage": "initializing",
            "created_at": datetime.now().isoformat(),
            "user_id": user_id,
            "request": request.dict()
        }
        
        # Start background task
        background_tasks.add_task(generate_video_task, job_id, user_id, request)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Video generation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get generation status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/api/videos")
async def get_videos(userId: int):
    """Get user's videos"""
    try:
        videos = get_user_videos(userId)
        
        return {
            "success": True,
            "videos": [
                {
                    "id": str(v['id']),
                    "topic": v['topic'],
                    "thumbnail": v.get('thumbnail_path', ''),
                    "duration": v.get('duration_seconds', 0),
                    "created_at": v['created_at'].isoformat() if v.get('created_at') else '',
                    "file_path": v['file_path']
                }
                for v in videos
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: int):
    """Delete a video"""
    try:
        # TODO: Implement video deletion
        # Delete from database and file system
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task for video generation
async def generate_video_task(job_id: str, user_id: int, request: GenerateRequest):
    """Background task to generate video using CommercialPipeline"""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["stage"] = "initializing"
        jobs[job_id]["progress"] = 10
        
        # TODO: Initialize CommercialPipeline
        # from commercial.pipeline import CommercialPipeline
        # from commercial.config import config
        # 
        # pipeline = CommercialPipeline(
        #     groq_api_key=config.GROQ_API_KEY,
        #     fal_api_key=config.FAL_API_KEY,
        #     elevenlabs_api_key=config.ELEVENLABS_API_KEY
        # )
        # 
        # def on_progress(progress):
        #     jobs[job_id]["stage"] = progress.stage
        #     jobs[job_id]["progress"] = int((progress.current / progress.total) * 100)
        # 
        # pipeline.set_progress_callback(on_progress)
        # 
        # result = pipeline.generate_video(
        #     topic=request.topic,
        #     style=request.style,
        #     aspect_ratio=request.aspect_ratio
        # )
        
        # Simulate for now
        import asyncio
        stages = [
            ("generating_story", 20),
            ("creating_images", 40),
            ("animating_scenes", 60),
            ("generating_voiceover", 80),
            ("assembling_video", 90),
        ]
        
        for stage, progress in stages:
            jobs[job_id]["stage"] = stage
            jobs[job_id]["progress"] = progress
            await asyncio.sleep(2)
        
        # Save to database
        video = save_video_metadata(
            user_id=user_id,
            topic=request.topic,
            file_path="/videos/output.mp4",  # TODO: Use actual path
            duration_seconds=30,
            metadata={
                "style": request.style,
                "aspect_ratio": request.aspect_ratio,
                "num_scenes": request.num_scenes
            }
        )
        
        # Increment usage
        increment_usage(user_id)
        
        # Mark complete
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["video_id"] = video['id']
        jobs[job_id]["video_url"] = video['file_path']
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"Generation error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
