# 🚀 Quick Deploy to Railway - Your Setup

## Your Infrastructure
- ✅ **Domain**: technov.ai (GoDaddy)
- ✅ **Database**: Supabase
- ✅ **Hosting**: Railway (GitHub connected)
- ✅ **Auth**: Firebase

## 🎯 Deploy in 10 Minutes

### 1. Push Latest Code ✅ (Already Done!)
```bash
git add .
git commit -m "Updated CORS for technov.ai"
git push
```

### 2. Railway - Add Backend Service

**Go to Railway Dashboard → Your Project**

1. Click **"New Service"** → **"GitHub Repo"**
2. Select **`omnicomni`** repository
3. Set **Root Directory**: `.` (leave empty or put a dot)
4. Click **"Add Variables"**

**Copy-paste these environment variables:**

```env
DATABASE_URL=postgresql://postgres:technovgnavin@db.zashqsgxushwoexvpqri.supabase.co:5432/postgres
GEMINI_API_KEY=AIzaSyAErVEKX8Xu3RGlLLINtd4gUQTWmH_SQuA
FAL_API_KEY=2778ef66-5cd9-4857-a708-df5104ded605:e01e50bcc194bf5362638bbd4a3da315
ELEVENLABS_API_KEY=sk_b2f35c77261b81d0a64a0cb8e4fb68b6c018f92a8aefb2e8
```

**Add your Firebase credentials** (get from your .env.commercial):
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_WEB_API_KEY=your-web-api-key
```

5. Click **"Deploy"**
6. **Copy the backend URL** (e.g., `https://omnicomni-production.up.railway.app`)

### 3. Railway - Add Frontend Service

1. Click **"New Service"** → **"GitHub Repo"**
2. Select **`omnicomni`** repository again
3. Set **Root Directory**: `web`
4. Click **"Add Variables"**

**Add these:**
```env
PYTHON_BACKEND_URL=https://your-backend-url.up.railway.app
NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
```
*(Replace with your actual backend URL from step 2)*

5. Click **"Deploy"**

### 4. Connect Domain (technov.ai)

1. Go to **Frontend Service** → **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Enter: `technov.ai`
4. Railway will show you DNS settings

**In GoDaddy DNS:**
- Add CNAME record:
  - **Type**: CNAME
  - **Name**: @ (or www)
  - **Value**: `your-app.up.railway.app`
  - **TTL**: 600

5. Wait 5-10 minutes for DNS propagation

### 5. Initialize Database (One-time)

**Option A - Via Railway Shell:**
1. Go to Backend service
2. Click "..." → "Shell"
3. Run:
```bash
python -c "from commercial.database import init_db; init_db()"
```

**Option B - Via Local Terminal:**
```bash
python -c "from commercial.database import init_db; init_db()"
```

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend service created in Railway
- [ ] Backend environment variables added
- [ ] Backend deployed successfully
- [ ] Backend URL copied
- [ ] Frontend service created in Railway
- [ ] Frontend environment variables added (with backend URL)
- [ ] Frontend deployed successfully
- [ ] Domain connected to frontend
- [ ] DNS updated in GoDaddy
- [ ] Database initialized
- [ ] Tested signup/login
- [ ] Tested video generation

## 🎉 You're Live!

Visit: **https://technov.ai**

Your new Next.js app is now live with:
- ✅ Beautiful modern UI
- ✅ Fast performance
- ✅ All Streamlit features + more
- ✅ Your existing Supabase database
- ✅ Your existing Firebase auth
- ✅ Custom domain with SSL

## 🔍 Quick Test

1. Go to https://technov.ai
2. Click "Sign Up"
3. Create account
4. Login
5. Try generating a video
6. Check your Supabase dashboard - you should see the new user!

## 💡 Pro Tips

- **Logs**: Check Railway logs if something doesn't work
- **Database**: Use Supabase dashboard to view data
- **Updates**: Just `git push` and Railway auto-deploys!

## 🆘 Need Help?

Check `RAILWAY_DEPLOYMENT.md` for detailed troubleshooting.

---

**That's it! Your app is live on technov.ai! 🚀**
