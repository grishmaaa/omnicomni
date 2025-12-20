# 🚀 Add Next.js to Your Existing Railway Project

## Your Current Setup (I can see it!)

✅ **Railway Project**: Already exists  
✅ **Domain**: technov.ai (connected to Port 8501 - Streamlit)  
✅ **Service**: web-production-f1795.up.railway.app  

## What We're Doing

We're going to **ADD** two new services to your existing Railway project:
1. **Backend Service** (FastAPI) - New Python API
2. **Frontend Service** (Next.js) - New modern UI

Then we'll **switch** technov.ai to point to the new Next.js frontend!

## 📋 Step-by-Step

### Step 1: Add Backend Service (FastAPI)

1. **In your Railway project**, click **"+ New"** → **"GitHub Repo"**
2. Select your **`omnicomni`** repository
3. **Important Settings**:
   - **Service Name**: `backend-api` (or whatever you want)
   - **Root Directory**: Leave empty (or put `.`)
   - **Start Command**: Will auto-detect from `Procfile`

4. **Add Environment Variables** (click "Variables" tab):

```env
# Supabase Database
DATABASE_URL=postgresql://postgres:technovgnavin@db.zashqsgxushwoexvpqri.supabase.co:5432/postgres

# Supabase Auth (get from Supabase Dashboard → Settings → API)
SUPABASE_URL=https://zashqsgxushwoexvpqri.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Keys (from your .env.commercial)
GEMINI_API_KEY=AIzaSyAErVEKX8Xu3RGlLLINtd4gUQTWmH_SQuA
FAL_API_KEY=2778ef66-5cd9-4857-a708-df5104ded605:e01e50bcc194bf5362638bbd4a3da315
ELEVENLABS_API_KEY=sk_b2f35c77261b81d0a64a0cb8e4fb68b6c018f92a8aefb2e8
```

5. Click **"Deploy"**
6. **Copy the backend URL** (e.g., `https://backend-api-production.up.railway.app`)

### Step 2: Add Frontend Service (Next.js)

1. **In same Railway project**, click **"+ New"** → **"GitHub Repo"**
2. Select your **`omnicomni`** repository again
3. **Important Settings**:
   - **Service Name**: `frontend-nextjs` (or whatever you want)
   - **Root Directory**: `web` ⚠️ **IMPORTANT!**
   - **Build Command**: Auto-detected (`npm run build`)
   - **Start Command**: Auto-detected (`npm start`)

4. **Add Environment Variables**:

```env
PYTHON_BACKEND_URL=https://backend-api-production.up.railway.app
NEXT_PUBLIC_API_URL=https://backend-api-production.up.railway.app
```
*(Replace with your actual backend URL from Step 1)*

5. Click **"Deploy"**
6. Railway will give you a URL like `https://frontend-nextjs-production.up.railway.app`

### Step 3: Switch technov.ai to New Frontend

**Option A: Update Existing Domain**
1. Go to your **new Next.js service** (frontend-nextjs)
2. Click **"Settings"** → **"Networking"**
3. Click **"Custom Domain"**
4. Enter: `technov.ai`
5. Railway will say "This domain is already in use"
6. Go to your **old Streamlit service** (web-production-f1795)
7. Remove `technov.ai` from there
8. Go back to Next.js service and add `technov.ai` again

**Option B: Use Subdomain First (Safer)**
1. Keep Streamlit on `technov.ai` for now
2. Add `app.technov.ai` to Next.js service
3. Test everything works
4. Then switch main domain later

### Step 4: Get Supabase ANON Key

1. Go to **Supabase Dashboard**: https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy the **anon public** key
5. Add it to Railway Backend variables as `SUPABASE_ANON_KEY`

### Step 5: Initialize Database (One-time)

**Via Railway Shell:**
1. Go to **Backend Service** in Railway
2. Click **"..."** menu → **"Shell"**
3. Run this command:
```bash
python -c "from commercial.database import init_db; init_db()"
```

This creates all the tables in your Supabase database.

## 🎯 Your Final Setup

After deployment, you'll have:

**Old (Keep for now):**
- `web-production-f1795.up.railway.app` - Streamlit (old UI)

**New:**
- `backend-api-production.up.railway.app` - FastAPI backend
- `frontend-nextjs-production.up.railway.app` - Next.js frontend
- `technov.ai` → Points to Next.js (or `app.technov.ai` if you use subdomain)

## ✅ Checklist

- [ ] Backend service added to Railway
- [ ] Backend environment variables set (Supabase URL, ANON_KEY, API keys)
- [ ] Backend deployed successfully
- [ ] Backend URL copied
- [ ] Frontend service added to Railway
- [ ] Frontend root directory set to `web`
- [ ] Frontend environment variables set (backend URL)
- [ ] Frontend deployed successfully
- [ ] Database initialized via shell
- [ ] Domain switched to new frontend (or subdomain added)
- [ ] Tested signup/login on new site
- [ ] Old Streamlit still accessible (as backup)

## 🧪 Testing

1. Visit your new Next.js URL (or technov.ai if you switched)
2. Click "Sign Up"
3. Create a test account
4. Login
5. Try the dashboard
6. Check Supabase dashboard - you should see the new user!

## 🔄 Rollback Plan

If something goes wrong:
1. Keep old Streamlit service running
2. Point technov.ai back to Streamlit
3. Debug new services
4. Switch back when ready

## 💡 Pro Tips

- **Don't delete** old Streamlit service yet - keep as backup!
- Test on Railway URLs first before switching domain
- Use `app.technov.ai` for testing if you want
- Check Railway logs if something doesn't work

## 🆘 Common Issues

**Backend won't start?**
- Check Railway logs
- Make sure `SUPABASE_ANON_KEY` is set
- Verify all environment variables are correct

**Frontend can't connect to backend?**
- Check `PYTHON_BACKEND_URL` is correct
- Make sure backend is running
- Check backend CORS allows your domain

**Database errors?**
- Make sure you ran `init_db()` command
- Check DATABASE_URL is correct
- Verify Supabase project is active

---

**You're adding the new Next.js app alongside your existing Streamlit!** 🚀

Both will run together until you're ready to fully switch over!
