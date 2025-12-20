# 🚀 Railway Deployment - Using Your Existing Setup

## Your Current Infrastructure

✅ **Domain**: technov.ai (GoDaddy)  
✅ **Database**: Supabase PostgreSQL  
✅ **Hosting**: Railway (already connected to GitHub)  
✅ **Auth**: Firebase  

## 🎯 What We're Deploying

1. **Python Backend** (FastAPI) - New API server
2. **Next.js Frontend** - New modern UI
3. **Connect to existing Supabase DB**
4. **Use existing Firebase Auth**
5. **Deploy to existing Railway project**

## 📋 Step-by-Step Deployment

### Step 1: Railway Backend Service

Since you already have Railway connected to GitHub, let's add the backend:

1. **Go to Railway Dashboard**
   - Open your existing project (the one connected to technov.ai)

2. **Add New Service**
   - Click "New Service" → "GitHub Repo"
   - Select `omnicomni` repository
   - Set **Root Directory**: `.` (root folder)
   - Railway will detect it's a Python app

3. **Add Environment Variables**

Click "Variables" tab and add these:

```env
# Supabase Database (you already have this!)
DATABASE_URL=postgresql://postgres:technovgnavin@db.zashqsgxushwoexvpqri.supabase.co:5432/postgres

# Firebase (from your .env.commercial)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_WEB_API_KEY=your-web-api-key

# Or use the full JSON (easier!)
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# API Keys (from your .env.commercial)
GEMINI_API_KEY=AIzaSyAErVEKX8Xu3RGlLLINtd4gUQTWmH_SQuA
FAL_API_KEY=2778ef66-5cd9-4857-a708-df5104ded605:e01e50bcc194bf5362638bbd4a3da315
ELEVENLABS_API_KEY=sk_b2f35c77261b81d0a64a0cb8e4fb68b6c018f92a8aefb2e8

# Port (Railway will set this automatically)
PORT=8000
```

4. **Deploy Backend**
   - Click "Deploy"
   - Wait for build to complete
   - Copy the backend URL: `https://your-backend.up.railway.app`

### Step 2: Railway Frontend Service

1. **Add Another Service**
   - Click "New Service" → "GitHub Repo"
   - Select `omnicomni` repository again
   - Set **Root Directory**: `web`
   - Railway will detect Next.js

2. **Add Environment Variables**

```env
# Point to your backend
PYTHON_BACKEND_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

3. **Deploy Frontend**
   - Click "Deploy"
   - Wait for build to complete

### Step 3: Connect Custom Domain (technov.ai)

You already have technov.ai connected to Railway, so:

1. **Go to Frontend Service**
   - Click "Settings" → "Domains"
   - You should see `technov.ai` already connected

2. **Update DNS if needed**
   - If not connected, add CNAME record in GoDaddy:
     ```
     Type: CNAME
     Name: @ (or www)
     Value: your-app.up.railway.app
     ```

3. **SSL Certificate**
   - Railway auto-generates SSL
   - Wait 5-10 minutes for propagation

### Step 4: Initialize Database

The database tables need to be created. Run this once:

1. **Option A: Via Railway Shell**
   - Go to Backend service
   - Click "..." → "Shell"
   - Run: `python -c "from commercial.database import init_db; init_db()"`

2. **Option B: Via Local Script**
   ```bash
   # Set your Supabase URL
   export DATABASE_URL="postgresql://postgres:technovgnavin@db.zashqsgxushwoexvpqri.supabase.co:5432/postgres"
   
   # Run initialization
   python -c "from commercial.database import init_db; init_db()"
   ```

## ✅ Environment Variables Checklist

### Backend Service
- [ ] `DATABASE_URL` (Supabase)
- [ ] `FIREBASE_CREDENTIALS_JSON` or individual Firebase vars
- [ ] `GEMINI_API_KEY`
- [ ] `FAL_API_KEY`
- [ ] `ELEVENLABS_API_KEY`
- [ ] `PORT` (auto-set by Railway)

### Frontend Service
- [ ] `PYTHON_BACKEND_URL`
- [ ] `NEXT_PUBLIC_API_URL`

## 🔧 Update Backend CORS

Make sure your backend allows requests from technov.ai:

In `api_server.py`, the CORS is already set to:
```python
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

Update it to:
```python
allow_origins=[
    "http://localhost:3000",
    "https://technov.ai",
    "https://www.technov.ai"
]
```

Then commit and push:
```bash
git add api_server.py
git commit -m "Update CORS for technov.ai"
git push
```

Railway will auto-deploy!

## 🎯 Your Final Setup

After deployment:

- **Frontend**: https://technov.ai (Next.js)
- **Backend**: https://your-backend.up.railway.app (FastAPI)
- **Database**: Supabase (already configured)
- **Auth**: Firebase (already configured)

## 🧪 Testing

1. **Visit**: https://technov.ai
2. **Test Signup**: Create a new account
3. **Test Login**: Login with your account
4. **Test Dashboard**: Try generating a video
5. **Check Database**: Verify users are created in Supabase

## 📊 Monitor in Railway

- **Logs**: Click on service → "Logs" tab
- **Metrics**: See CPU, memory, requests
- **Deployments**: View deployment history

## 💰 Cost

Since you're already on Railway:
- **Backend**: ~$5-10/month (new service)
- **Frontend**: ~$5-10/month (new service)
- **Supabase**: Free tier (you're already using)
- **Total**: ~$10-20/month additional

## 🔍 Troubleshooting

### Backend won't start?
```bash
# Check Railway logs
# Common issues:
1. Missing environment variables
2. Wrong DATABASE_URL
3. Firebase credentials not set
```

### Frontend can't connect?
```bash
# Make sure:
1. PYTHON_BACKEND_URL points to backend
2. Backend CORS allows technov.ai
3. Both services are running
```

### Database errors?
```bash
# Verify:
1. Supabase DATABASE_URL is correct
2. Database tables are initialized
3. Supabase project is active
```

## 🎉 You're Done!

Your app is now live at **https://technov.ai** with:
- ✅ Modern Next.js UI
- ✅ FastAPI backend
- ✅ Supabase database
- ✅ Firebase authentication
- ✅ Custom domain
- ✅ SSL certificate

Much better than Streamlit! 🚀
