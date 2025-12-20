# Railway Deployment Guide 🚂

Complete guide to deploy your AI Video Generator to Railway.

## 🎯 What We'll Deploy

1. **Next.js Frontend** - Your beautiful UI
2. **Python FastAPI Backend** - API server with database
3. **PostgreSQL Database** - Railway's managed database

## 📋 Prerequisites

1. Railway account (sign up at railway.app)
2. GitHub account (to connect your repo)
3. All environment variables ready

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

First, make sure your code is in a Git repository:

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Next.js migration complete"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/your-repo.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy PostgreSQL Database

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Click "Provision PostgreSQL"
4. Railway will create a database and give you connection details
5. Copy the `DATABASE_URL` - you'll need this!

### Step 3: Deploy Python Backend

1. In Railway, click "New Service" → "GitHub Repo"
2. Select your repository
3. Railway will auto-detect it's a Python app
4. Add these environment variables:

```env
# Database (automatically provided by Railway if you linked the DB)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Firebase
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
FIREBASE_WEB_API_KEY=your-web-api-key

# API Keys
GROQ_API_KEY=your-groq-key
FAL_API_KEY=your-fal-key
ELEVENLABS_API_KEY=your-elevenlabs-key
OPENAI_API_KEY=your-openai-key

# Python app settings
PORT=8000
```

5. Add a `Procfile` in your root directory (already exists):
```
web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

6. Click "Deploy"
7. Copy the backend URL (e.g., `https://your-app.railway.app`)

### Step 4: Deploy Next.js Frontend

1. In Railway, click "New Service" → "GitHub Repo"
2. Select your repository again
3. Set the **Root Directory** to `web`
4. Add environment variables:

```env
PYTHON_BACKEND_URL=https://your-backend.railway.app
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

5. Railway will auto-detect Next.js and deploy
6. Your frontend will be live at `https://your-frontend.railway.app`

### Step 5: Link Database to Backend

1. In Railway, go to your Python backend service
2. Click "Variables" tab
3. Click "Reference" → Select your PostgreSQL database
4. This automatically adds `DATABASE_URL` to your backend

## 📝 Required Files

### 1. `requirements.txt` (Root directory)

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
psycopg2-binary==2.9.9
firebase-admin==6.4.0
python-dotenv==1.0.0
pydantic==2.5.3
requests==2.31.0
```

### 2. `Procfile` (Root directory)

```
web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

### 3. `railway.json` (Root directory)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api_server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4. `web/package.json` (Already exists)

Make sure it has the build script:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

## 🔧 Environment Variables Reference

### Backend (Python)
```env
DATABASE_URL=postgresql://user:pass@host:port/db
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
FIREBASE_WEB_API_KEY=your-key
GROQ_API_KEY=your-key
FAL_API_KEY=your-key
ELEVENLABS_API_KEY=your-key
OPENAI_API_KEY=your-key
PORT=8000
```

### Frontend (Next.js)
```env
PYTHON_BACKEND_URL=https://your-backend.railway.app
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 🎨 Custom Domain (Optional)

1. Go to your service in Railway
2. Click "Settings" → "Domains"
3. Click "Generate Domain" or add custom domain
4. For custom domain:
   - Add your domain
   - Update DNS records as shown
   - Wait for SSL certificate

## 🔍 Troubleshooting

### Backend won't start?
```bash
# Check logs in Railway dashboard
# Common issues:
1. Missing environment variables
2. Database not linked
3. Wrong PORT variable
```

### Frontend can't connect to backend?
```bash
# Make sure:
1. PYTHON_BACKEND_URL is set correctly
2. Backend is deployed and running
3. CORS is configured in api_server.py
```

### Database connection failed?
```bash
# Check:
1. DATABASE_URL is set
2. Database service is running
3. psycopg2-binary is in requirements.txt
```

## 📊 Monitoring

Railway provides:
- Real-time logs
- Metrics dashboard
- Resource usage
- Deployment history

Access via Railway dashboard → Your Service → Logs/Metrics

## 💰 Pricing

Railway offers:
- **Free Tier**: $5 free credits/month
- **Pro Plan**: $20/month + usage
- **Database**: ~$5-10/month

Estimated monthly cost: **$10-15** for small-medium traffic

## 🚀 Quick Deploy Commands

```bash
# 1. Commit your code
git add .
git commit -m "Ready for Railway deployment"
git push

# 2. Railway will auto-deploy on push

# 3. Check deployment status
railway status

# 4. View logs
railway logs
```

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created in Railway
- [ ] Backend service deployed
- [ ] Backend environment variables set
- [ ] Database linked to backend
- [ ] Frontend service deployed
- [ ] Frontend environment variables set
- [ ] Both services running
- [ ] Test login/signup
- [ ] Test video generation
- [ ] Custom domain configured (optional)

## 🎉 You're Live!

Once deployed, your app will be accessible at:
- Frontend: `https://your-app.railway.app`
- Backend: `https://your-backend.railway.app`

Share the frontend URL with your users! 🚀

## 📝 Post-Deployment

1. **Test everything**
   - Login/Signup
   - Video generation
   - Video library
   - Profile page

2. **Monitor logs**
   - Check for errors
   - Monitor performance
   - Track usage

3. **Set up alerts**
   - Railway can notify you of issues
   - Set up Sentry for error tracking

4. **Scale as needed**
   - Railway auto-scales
   - Upgrade plan if needed

---

**Need help?** Check Railway docs or the logs in your dashboard!
