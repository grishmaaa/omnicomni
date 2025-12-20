# ✅ EXACT STEPS - Deploy Next.js to Railway (5 Minutes)

## Your Situation
- ✅ Railway project exists
- ✅ GitHub connected
- ✅ technov.ai domain connected
- ✅ Currently running Streamlit

## What We're Doing
**Convert your existing service to run the backend, add a new service for frontend.**

---

## 🎯 STEP 1: Update Existing Service (Backend)

### 1.1 Go to Railway
- Open https://railway.app
- Click your project
- Click your service (`web-production-f1795`)

### 1.2 Change Settings
Click **"Settings"** tab:

- **Root Directory**: Leave empty or put `.`
- **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
- Click **"Save Changes"**

### 1.3 Add Environment Variables
Click **"Variables"** tab, click **"+ New Variable"**, add these ONE BY ONE:

```
DATABASE_URL
postgresql://postgres:technovgnavin@db.zashqsgxushwoexvpqri.supabase.co:5432/postgres
```

```
SUPABASE_URL
https://zashqsgxushwoexvpqri.supabase.co
```

```
SUPABASE_ANON_KEY
(Get from Supabase Dashboard → Settings → API → anon public key)
```

```
GEMINI_API_KEY
AIzaSyAErVEKX8Xu3RGlLLINtd4gUQTWmH_SQuA
```

```
FAL_API_KEY
2778ef66-5cd9-4857-a708-df5104ded605:e01e50bcc194bf5362638bbd4a3da315
```

```
ELEVENLABS_API_KEY
sk_b2f35c77261b81d0a64a0cb8e4fb68b6c018f92a8aefb2e8
```

### 1.4 Deploy
- Railway will auto-deploy
- Wait for "Success" ✅
- **Copy the service URL** (e.g., `https://web-production-f1795.up.railway.app`)

---

## 🎯 STEP 2: Add Frontend Service

### 2.1 Create New Service
- In same Railway project
- Click **"+ New"** button (top right)
- Click **"GitHub Repo"**
- Select your **`omnicomni`** repository
- Click **"Add Service"**

### 2.2 Configure Service
Click **"Settings"** tab:

- **Service Name**: `frontend` (or whatever you want)
- **Root Directory**: `web` ⚠️ **IMPORTANT!**
- **Build Command**: `npm run build` (auto-detected)
- **Start Command**: `npm start` (auto-detected)
- Click **"Save Changes"**

### 2.3 Add Environment Variables
Click **"Variables"** tab, add:

```
PYTHON_BACKEND_URL
https://web-production-f1795.up.railway.app
```
*(Use the URL you copied from Step 1.4)*

```
NEXT_PUBLIC_API_URL
https://web-production-f1795.up.railway.app
```
*(Same URL)*

### 2.4 Deploy
- Railway will auto-deploy
- Wait for "Success" ✅

---

## 🎯 STEP 3: Move Domain to Frontend

### 3.1 Remove from Old Service
- Go to **backend service** (web-production-f1795)
- Click **"Settings"** → **"Networking"**
- Find `technov.ai`
- Click **"Remove"** (trash icon)

### 3.2 Add to New Service
- Go to **frontend service**
- Click **"Settings"** → **"Networking"**
- Click **"Custom Domain"**
- Enter: `technov.ai`
- Click **"Add"**

### 3.3 Wait
- DNS propagation: 5-10 minutes
- Railway will show "Active" when ready

---

## 🎯 STEP 4: Initialize Database (One-Time)

### 4.1 Open Backend Shell
- Go to **backend service**
- Click **"..."** menu (top right)
- Click **"Shell"**

### 4.2 Run Command
In the shell, type:
```bash
python -c "from commercial.database import init_db; init_db()"
```
Press Enter. You should see "✅ Database tables created successfully"

---

## ✅ DONE!

Visit **https://technov.ai** - you should see your new Next.js app!

### Test It:
1. Click "Sign Up"
2. Create account
3. Login
4. Try dashboard

---

## 🆘 If Something Goes Wrong

**Backend won't start?**
- Check Railway logs (click service → "Deployments" → latest → "View Logs")
- Make sure all environment variables are set
- Check `SUPABASE_ANON_KEY` is correct

**Frontend won't start?**
- Check Root Directory is `web`
- Check `PYTHON_BACKEND_URL` is correct
- Check backend is running

**Can't access technov.ai?**
- Wait 10 minutes for DNS
- Check domain is added to frontend service
- Try clearing browser cache

---

## 📊 Final Setup

```
Railway Project
├── web-production-f1795 (Backend - Python API)
│   └── https://web-production-f1795.up.railway.app
└── frontend (Frontend - Next.js)
    └── https://technov.ai ✨
```

**You're live!** 🚀
