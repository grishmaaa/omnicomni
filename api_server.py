#
# api_server.py (Complete File)
#
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import sys
from pathlib import Path
import os
from fastapi.staticfiles import StaticFiles

# --- Basic Setup ---
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

app = FastAPI(title="AI Video Generator API")
jobs = {}

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for debugging, can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files for Videos ---
output_dir = project_root / "commercial" / "output"
output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=output_dir), name="videos")

# --- Database & Auth Imports (moved inside functions to avoid startup errors) ---

# --- Pydantic Models ---
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

# --- Background Task (ULTRA-ROBUST LOGGING) ---
async def generate_video_task(job_id: str, user_id: int, request: GenerateRequest):
    print(f"✅✅✅ JOB {job_id}: Background task function has been entered by FastAPI.")
    try:
        # Import everything INSIDE the try block to catch import errors
        print(f"   JOB {job_id}: STEP 1 - Importing dependencies...")
        from commercial.pipeline import CommercialPipeline
        from commercial.config import config
        from commercial.database import save_video_metadata, increment_usage
        print(f"   JOB {job_id}: STEP 1 - Imports successful.")

        # Initialize pipeline
        print(f"   JOB {job_id}: STEP 2 - Initializing CommercialPipeline...")
        pipeline = CommercialPipeline(
            openai_api_key=config.OPENAI_API_KEY,
            fal_api_key=config.FAL_API_KEY,
            elevenlabs_api_key=config.ELEVENLABS_API_KEY
        )
        print(f"   JOB {job_id}: STEP 2 - Pipeline initialized.")

        def on_progress(progress):
            print(f"   PROGRESS {job_id}: [{progress.stage}] {progress.current}/{progress.total}")
            jobs[job_id]["stage"] = progress.stage
            jobs[job_id]["message"] = progress.message
            stage_map = {"story": 0, "images": 20, "videos": 40, "voice": 70, "assembly": 90}
            base_progress = stage_map.get(progress.stage, 0)
            stage_progress = (progress.current / progress.total) if progress.total > 0 else 0
            jobs[job_id]["progress"] = int(base_progress + (stage_progress * 20))

        pipeline.set_progress_callback(on_progress)
        
        # Run generation
        print(f"   JOB {job_id}: STEP 3 - Starting main generate_video() process...")
        result = pipeline.generate_video(
            topic=request.topic, style=request.style, aspect_ratio=request.aspect_ratio
        )
        print(f"   JOB {job_id}: STEP 3 - Generation process finished.")
        
        # Process results
        print(f"   JOB {job_id}: STEP 4 - Processing results and saving to DB...")
        final_path = Path(result['final_video'])
        relative_path = final_path.relative_to(output_dir)
        web_url = f"/videos/{relative_path}".replace("\\", "/")

        video_meta = save_video_metadata(
            user_id=user_id, topic=request.topic, file_path=web_url,  
            duration_seconds=int(result['duration_seconds']),
            metadata={"style": request.style, "cost": result['total_cost']}
        )
        
        increment_usage(user_id)
        print(f"   JOB {job_id}: STEP 4 - Database updated.")
        
        # Mark complete
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["video_id"] = video_meta['id']
        jobs[job_id]["video_url"] = web_url
        print(f"✅✅✅ JOB {job_id}: Task COMPLETED successfully!")

    except Exception as e:
        print(f"❌❌❌ JOB {job_id}: FATAL ERROR in background task! ❌❌❌")
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"A critical error occurred: {str(e)}"

# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    print("INFO:     Application startup complete.")
    try:
        from commercial.database import init_db
        init_db()
        print("✅ Database initialized on startup.")
    except Exception as e:
        print(f"⚠️ Database initialization failed on startup: {e}")

@app.get("/")
async def root():
    return {"status": "online", "service": "Technov.ai Backend API"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    try:
        from commercial.auth_supabase import verify_password
        from commercial.database import get_user_by_uid, create_user, update_last_login, get_user_subscription, create_subscription
        
        user_data = verify_password(request.email, request.password)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        db_user = get_user_by_uid(user_data['uid'])
        if not db_user:
            db_user = create_user(user_data['uid'], user_data['email'], user_data.get('display_name', ''))
        
        update_last_login(user_data['uid'])
        subscription = get_user_subscription(db_user['id']) or create_subscription(db_user['id'], 'free')
        
        return {"success": True, "user": db_user, "subscription": subscription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    try:
        from commercial.auth_supabase import signup_user
        from commercial.database import create_user
        from commercial.subscription import create_subscription
        
        user_data = signup_user(request.email, request.password, request.name)
        db_user = create_user(user_data['uid'], user_data['email'], request.name)
        subscription = create_subscription(db_user['id'], request.plan)
        
        return {"success": True, "user": db_user, "subscription": subscription}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate")
async def generate_video_endpoint(request: GenerateRequest, background_tasks: BackgroundTasks):
    print("INFO:     Received POST request for /api/generate")
    # TODO: Get user from a real session/token
    user_id = 1  # Hardcoded for now
    
    try:
        from commercial.subscription import can_generate_video
        
        # Check usage limits
        # can_generate, message = can_generate_video(user_id, 'pro') # Mocking pro for now
        # if not can_generate:
        #     raise HTTPException(status_code=403, detail=message)
        
        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "queued", "progress": 0, "stage": "queued", "message": "Request accepted..."}
        
        print(f"   - Queuing job {job_id}...")
        background_tasks.add_task(generate_video_task, job_id, user_id, request)
        print(f"   - Job {job_id} has been successfully handed off to background worker.")
        
        # Immediately return the job_id
        return {"success": True, "job_id": job_id, "message": "Video generation started"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR:     Failed to queue generation task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {e}")

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/api/videos")
async def get_videos(userId: int):
    try:
        from commercial.database import get_user_videos
        videos = get_user_videos(userId)
        return {"success": True, "videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)