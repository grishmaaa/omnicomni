# 🔄 Replace Streamlit with Next.js - Same Railway Service

## Super Simple: Just Update Your Existing Service!

You already have Railway connected to GitHub and technov.ai working.  
We'll just **change what it runs** - from Streamlit to Next.js!

## 🎯 Quick Steps (5 minutes)

### Step 1: Update Your Existing Service

1. **Go to Railway Dashboard**
2. Click on your **existing service** (`web-production-f1795`)
3. Go to **"Settings"** tab

### Step 2: Change Root Directory

1. In Settings, find **"Root Directory"**
2. Change from: ` ` (empty - runs Streamlit)
3. Change to: `web` (runs Next.js)
4. Click **"Save"**

### Step 3: Add Environment Variables

1. Click **"Variables"** tab
2. **Delete** old Streamlit variables (if any)
3. **Add** these new ones:

```env
# Backend API (we'll add this service next)
PYTHON_BACKEND_URL=https://web-production-f1795.up.railway.app/api
NEXT_PUBLIC_API_URL=https://web-production-f1795.up.railway.app/api
```

Wait - actually, let's run BOTH frontend and backend in ONE service!

### Better Approach: Run Both in One Service

Actually, let's keep it even simpler. Let me create a startup script that runs both!

## ✅ Even Simpler: One Service, Both Apps

Let me create a file that runs both Next.js frontend AND Python backend together:

### Step 1: I'll Create a Startup Script

Create `start.sh` in your root:

```bash
#!/bin/bash
# Start backend in background
cd /app
python api_server.py &

# Start frontend
cd /app/web
npm run build
npm start
```

### Step 2: Update Procfile

Change your `Procfile` to:
```
web: chmod +x start.sh && ./start.sh
```

### Step 3: Railway Will Auto-Deploy

1. Push to GitHub
2. Railway auto-deploys
3. technov.ai now shows Next.js!

---

**Wait, this is getting complicated. Let me give you the SIMPLEST solution:**

## 🎯 SIMPLEST SOLUTION: Two Services (But Easy!)

### Service 1: Backend (Update Existing)

1. **Your existing Railway service**
2. Settings → Root Directory: ` ` (empty)
3. Settings → Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
4. Variables → Add:
```env
DATABASE_URL=postgresql://postgres:technovgnavin@db.zashqsgxushwoexvpqri.supabase.co:5432/postgres
SUPABASE_URL=https://zashqsgxushwoexvpqri.supabase.co
SUPABASE_ANON_KEY=your-key-from-supabase
GEMINI_API_KEY=AIzaSyAErVEKX8Xu3RGlLLINtd4gUQTWmH_SQuA
FAL_API_KEY=2778ef66-5cd9-4857-a708-df5104ded605:e01e50bcc194bf5362638bbd4a3da315
ELEVENLABS_API_KEY=sk_b2f35c77261b81d0a64a0cb8e4fb68b6c018f92a8aefb2e8
```

### Service 2: Frontend (New - 2 clicks!)

1. Railway → **"+ New"** → **"GitHub Repo"**
2. Select `omnicomni`
3. Root Directory: `web`
4. Variables:
```env
PYTHON_BACKEND_URL=https://web-production-f1795.up.railway.app
```
5. Settings → Domains → Add `technov.ai`

**Done! technov.ai now shows Next.js!**

---

Which approach do you prefer? I can create exact steps for whichever is easier for you!
