# 🚂 Quick Railway Deployment - TL;DR

## Super Fast Setup (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push
```

### 2. Railway Setup

**Go to [railway.app](https://railway.app) and:**

1. **Create Database**
   - New Project → Provision PostgreSQL
   - Copy the `DATABASE_URL`

2. **Deploy Backend**
   - New Service → GitHub Repo → Select your repo
   - Set Root Directory: `.` (root)
   - Add Environment Variables:
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     FIREBASE_CREDENTIALS_JSON=your-json
     FIREBASE_WEB_API_KEY=your-key
     GROQ_API_KEY=your-key
     FAL_API_KEY=your-key
     ELEVENLABS_API_KEY=your-key
     ```
   - Link to PostgreSQL database
   - Deploy!
   - Copy backend URL: `https://xxx.railway.app`

3. **Deploy Frontend**
   - New Service → GitHub Repo → Same repo
   - Set Root Directory: `web`
   - Add Environment Variables:
     ```
     PYTHON_BACKEND_URL=https://your-backend.railway.app
     ```
   - Deploy!
   - Copy frontend URL: `https://xxx.railway.app`

### 3. Done! 🎉

Visit your frontend URL and start using your app!

## Files Already Created ✅

- ✅ `Procfile` - Tells Railway how to run backend
- ✅ `railway.json` - Railway configuration
- ✅ `requirements.backend.txt` - Python dependencies
- ✅ `web/package.json` - Next.js dependencies

## Environment Variables Needed

### Backend
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
FIREBASE_WEB_API_KEY=your-key
GROQ_API_KEY=your-key
FAL_API_KEY=your-key
ELEVENLABS_API_KEY=your-key
```

### Frontend
```env
PYTHON_BACKEND_URL=https://your-backend.railway.app
```

## Cost
- **Free Tier**: $5/month credits (enough for testing)
- **Paid**: ~$10-15/month for production

## Troubleshooting

**Backend won't start?**
- Check logs in Railway dashboard
- Make sure all env vars are set
- Verify database is linked

**Frontend can't connect?**
- Check `PYTHON_BACKEND_URL` is correct
- Make sure backend is running

**Database errors?**
- Verify `DATABASE_URL` is set
- Check database service is running

## That's It!

Your app is now live on Railway! 🚀

Full guide: See `RAILWAY_DEPLOYMENT.md`
