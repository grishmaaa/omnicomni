# 🚂 Railway Deployment - Quick Reference

## 📋 Pre-Deployment Checklist
- [ ] Code pushed to GitHub (private repository)
- [ ] `.gitignore` excludes sensitive files
- [ ] `requirements.txt` generated
- [ ] Firebase credentials ready
- [ ] Database URL from Supabase
- [ ] All API keys documented

## 🚀 Deployment Steps

### 1. GitHub Setup
```bash
cd c:\Users\grish\OneDrive\Desktop\omnicomnimodel
git init
git add .
git commit -m "Initial commit - AI Video Generator"
git remote add origin https://github.com/YOUR_USERNAME/ai-video-generator.git
git push -u origin main
```

### 2. Railway Setup
1. Go to https://railway.app/
2. Sign up with GitHub
3. New Project → Deploy from GitHub repo
4. Select: `ai-video-generator`

### 3. Environment Variables (Railway Dashboard)
```bash
DATABASE_URL=postgresql://postgres:PASSWORD@db.zashqsgxushwoexvpqri.supabase.co:6543/postgres
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
FAL_KEY=your_fal_key
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GROQ_API_KEY=your_groq_key
ENVIRONMENT=production
```

### 4. Custom Domain (GoDaddy)
**Railway:**
- Settings → Domains → Custom Domain
- Enter: `app.yourdomain.com`
- Copy CNAME target

**GoDaddy:**
- DNS Management → Add Record
- Type: CNAME
- Name: `app`
- Value: `your-app-production.up.railway.app`
- TTL: 600

### 5. Verify
- Wait 10-30 minutes for DNS
- Visit: `https://app.yourdomain.com`
- Test signup, login, video generation

## 🔧 Common Commands

### Update Deployment
```bash
git add .
git commit -m "Update: description"
git push
# Railway auto-deploys!
```

### Check Logs
Railway Dashboard → Deployments → Latest → View Logs

### Rollback
Railway Dashboard → Deployments → Previous → Redeploy

## 💰 Costs
- First month: FREE ($5 credit)
- After: ~$5-10/month

## 📞 Support
- Railway: https://docs.railway.app/
- Discord: https://discord.gg/railway

## ✅ Success Indicators
- [ ] Railway shows "Success" status
- [ ] Custom domain resolves
- [ ] App loads at your domain
- [ ] Can sign up/login
- [ ] Video generation works
- [ ] Database connected
- [ ] Firebase auth working
