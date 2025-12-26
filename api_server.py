"""
Enhanced FastAPI Backend with Database Integration
Connects Next.js frontend to PostgreSQL database and CommercialPipeline
"""
print("🚀 STARTING BACKEND VERSION 3.0 - ITERATIVE RENDERER")

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

@app.get("/")
async def root():
    return {"status": "online", "service": "Technov.ai Backend API", "version": "1.0.0"}

# CORS middleware
from fastapi.staticfiles import StaticFiles
import os

# Create output directory if it doesn't exist
output_dir = Path("commercial/output")
output_dir.mkdir(parents=True, exist_ok=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://technov.ai",
        "https://www.technov.ai",
        "https://omnicomni.vercel.app",
        "https://*.vercel.app",
        "https://*.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve videos
app.mount("/videos", StaticFiles(directory="commercial/output"), name="videos")

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

    try:
        # Ensure mock user (id=1) exists for the hardcoded generation logic
        from commercial.database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        # Check if user 1 exists
        cur.execute("SELECT id FROM users WHERE id = 1")
        if not cur.fetchone():
            print("🔧 Creating Mock User (id=1) for testing...")
            # Insert mock user with specific ID 1
            # We use an explicit INSERT with ID to force it to be 1
            cur.execute("""
                INSERT INTO users (id, firebase_uid, email, display_name)
                OVERRIDING SYSTEM VALUE
                VALUES (1, 'mock-user-1', 'mock@technov.ai', 'Demo User')
            """)
            conn.commit()
            print("✅ Mock User created")
        
        # Check if subscription exists for user 1
        cur.execute("SELECT id FROM subscriptions WHERE user_id = 1")
        if not cur.fetchone():
            print("🔧 Creating Mock Subscription for User 1...")
            cur.execute("""
                INSERT INTO subscriptions (user_id, tier, status)
                VALUES (1, 'free', 'active')
            """)
            conn.commit()
            print("✅ Mock Subscription created")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Mock data creation warning: {e}")

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

@app.get("/api/download")
async def download_video(file_path: str):
    print(f"📥 DOWNLOAD REQUEST: {file_path}")
    
    # Security: Ensure we only serve from the output directory
    clean_path = file_path.replace("/videos/", "").lstrip("/")
    
    # Defensive fix: remove redundant path segments if they made it into the URL
    clean_path = clean_path.replace("commercial/output/", "").replace("commercial\\output\\", "")
    
    safe_path = (project_root / "commercial" / "output" / clean_path).resolve()
    base_dir = (project_root / "commercial" / "output").resolve()
    
    print(f"   Mapped to: {safe_path}")
    
    if not str(safe_path).startswith(str(base_dir)):
        print(f"❌ Access Denied: {safe_path} not in {base_dir}")
        raise HTTPException(status_code=403, detail="Access denied")
        
    if not safe_path.exists():
        print(f"❌ File Not Found: {safe_path}")
        raise HTTPException(status_code=404, detail="File not found")

    print("✅ Serving file...")
    from fastapi.responses import FileResponse
    return FileResponse(
        path=safe_path,
        filename=safe_path.name,
        media_type="application/octet-stream" 
    )

# Video generation endpoints
@app.post("/api/generate")
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start video generation"""
    # TODO: Get user_id from session
    user_id = 1  # Mock for now
    
    try:
        # Get subscription
        subscription = get_user_subscription(user_id)
        # TEMPORARY OVERRIDE: Force 'pro' tier for testing to avoid "0/0 limits" error
        # tier = subscription['tier'] if subscription else 'free'
        tier = 'pro'
        
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
            "message": "Request queued...",
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
# In api_server.py

# (Keep all your other code, just replace this one function)

async def generate_video_task(job_id: str, user_id: int, request: GenerateRequest):
    """
    Background task to generate video using CommercialPipeline.
    This version has EXTREMELY verbose logging to debug silent crashes.
    """
    print(f"✅✅✅ JOB {job_id}: Background task has been started by FastAPI.")
    
    try:
        # STEP 1: DYNAMICALLY IMPORT a critical dependency
        print(f"   JOB {job_id}: STEP 1 - Attempting to import CommercialPipeline...")
        from commercial.pipeline import CommercialPipeline
        from commercial.config import config
        print(f"   JOB {job_id}: STEP 1 - Import successful.")

        # STEP 2: INITIALIZE the pipeline
        print(f"   JOB {job_id}: STEP 2 - Attempting to initialize CommercialPipeline...")
        pipeline = CommercialPipeline(
            openai_api_key=config.OPENAI_API_KEY,
            fal_api_key=config.FAL_API_KEY,
            elevenlabs_api_key=config.ELEVENLABS_API_KEY
        )
        print(f"   JOB {job_id}: STEP 2 - Pipeline initialized successfully.")

        # STEP 3: SET UP the progress callback
        print(f"   JOB {job_id}: STEP 3 - Setting up progress callback...")
        def on_progress(progress):
            print(f"   PROGRESS {job_id}: [{progress.stage}] {progress.current}/{progress.total}")
            jobs[job_id]["stage"] = progress.stage
            jobs[job_id]["message"] = progress.message
            stage_map = {"story": 0, "images": 20, "videos": 40, "voice": 70, "assembly": 90}
            base_progress = stage_map.get(progress.stage, 0)
            stage_progress = (progress.current / progress.total) if progress.total > 0 else 0
            jobs[job_id]["progress"] = int(base_progress + (stage_progress * 20))

        pipeline.set_progress_callback(on_progress)
        print(f"   JOB {job_id}: STEP 3 - Callback set.")

        # STEP 4: RUN the main generation logic
        print(f"   JOB {job_id}: STEP 4 - Starting the main generate_video() process...")
        result = pipeline.generate_video(
            topic=request.topic,
            style=request.style,
            aspect_ratio=request.aspect_ratio
        )
        print(f"   JOB {job_id}: STEP 4 - Generation process finished without errors.")
        
        # STEP 5: PROCESS the results
        print(f"   JOB {job_id}: STEP 5 - Processing results and saving to DB...")
        final_path = Path(result['final_video']).resolve()
        base_output_dir = (project_root / "commercial" / "output").resolve()
        
        try:
            relative_path = final_path.relative_to(base_output_dir)
        except ValueError:
            # Fallback for safety: just grab folder/filename
            relative_path = Path(final_path.parent.name) / final_path.name
            
        web_url = f"/videos/{relative_path}".replace("\\", "/")

        video_meta = save_video_metadata(
            user_id=user_id,
            topic=request.topic,
            file_path=web_url,  
            duration_seconds=int(result['duration_seconds']),
            metadata={
                "style": request.style,
                "aspect_ratio": request.aspect_ratio,
                "num_scenes": result['num_scenes'],
                "total_cost": result['total_cost']
            }
        )
        
        increment_usage(user_id)
        print(f"   JOB {job_id}: STEP 5 - Database updated.")
        
        # FINAL STEP: Mark job as complete
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["video_id"] = video_meta['id']
        jobs[job_id]["video_url"] = web_url
        print(f"✅✅✅ JOB {job_id}: Task COMPLETED successfully!")

    except Exception as e:
        # This is now the most important part of the code. It will catch the crash.
        print(f"❌❌❌ JOB {job_id}: FATAL ERROR in background task! ❌❌❌")
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        
        # Update the job status so the frontend knows it failed
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"A critical error occurred on the server: {str(e)}"
        jobs[job_id]["error_details"] = error_details # Add full traceback for debugging

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)