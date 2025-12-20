# ⚡ FASTEST WAY: Update Existing Railway Service

## What You'll Do (Literally 3 Steps)

Your existing Railway service will switch from Streamlit to Next.js.  
**technov.ai stays connected** - no domain changes needed!

## 🚀 Steps (2 Minutes)

### 1. Update Service Settings

**In Railway Dashboard:**

1. Click your service (`web-production-f1795`)
2. Go to **Settings** tab
3. Find **"Root Directory"**
4. Change to: `web`
5. Find **"Start Command"** 
6. Change to: `npm run build && npm start`
7. Click **Save**

### 2. Update Environment Variables

**In Variables tab:**

Delete all old variables, add these:

```env
PYTHON_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=https://web-production-f1795.up.railway.app/api
```

### 3. Deploy!

Railway will auto-redeploy. Wait 2-3 minutes.

**Done! technov.ai now shows your Next.js app!** 🎉

---

## ⚠️ Wait - You Need Backend Too!

Next.js needs the Python backend API. Here's what to do:

### Option A: Add One More Service (Recommended - 2 clicks)

1. Railway → **"+ New"** → **"GitHub Repo"**
2. Select your repo
3. Root Directory: ` ` (empty - runs Python)
4. Add variables (Supabase keys, API keys)
5. Copy the backend URL
6. Update frontend `PYTHON_BACKEND_URL` to point to it

### Option B: Run Both in One Service (Advanced)

I can create a script that runs both Python backend and Next.js frontend together in one service.

---

## 🎯 My Recommendation

**Do this:**

1. **Keep existing service** for backend (Python API)
   - Change Start Command to: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - Add Supabase/API keys
   
2. **Add ONE new service** for frontend (Next.js)
   - Root Directory: `web`
   - Point to backend URL
   - Move `technov.ai` domain to this service

**Total time: 5 minutes. No complex setup.**

Want me to write exact click-by-click instructions for this?
