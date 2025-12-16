# AI Video Generator - Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-production.txt
```

### 2. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project (or use existing)
3. Enable **Authentication** → **Email/Password** provider
4. Go to **Project Settings** → **Service Accounts**
5. Click **"Generate new private key"**
6. Download the JSON file
7. Copy values to `.env.commercial`:
   ```bash
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY_ID=...
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@your-project.iam.gserviceaccount.com
   ```
8. Get **Web API Key** from **Project Settings** → **General**
   ```bash
   FIREBASE_WEB_API_KEY=AIza...
   ```

### 3. Setup PostgreSQL

**Option A: Cloud Service (Recommended)**

- **Supabase** (Free tier): https://supabase.com
  1. Create project
  2. Copy connection string from Settings → Database
  3. Add to `.env.commercial`:
     ```bash
     DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
     ```

- **Neon** (Serverless): https://neon.tech
- **Railway**: https://railway.app

**Option B: Local Installation**

1. Install PostgreSQL: https://www.postgresql.org/download/
2. Create database:
   ```sql
   CREATE DATABASE video_generator;
   ```
3. Add credentials to `.env.commercial`:
   ```bash
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=video_generator
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   ```

### 4. Initialize Database

```bash
python -c "from commercial.database import init_db; init_db()"
```

### 5. Test Firebase Connection

```bash
python -c "from commercial.auth import init_firebase; init_firebase(); print('✅ Firebase connected')"
```

### 6. Run the App

```bash
cd commercial
streamlit run app.py
```

The app will open at http://localhost:8501

---

## Environment Variables

Copy `.env.commercial.example` to `.env.commercial` and fill in:

```bash
# API Keys (existing)
OPENAI_API_KEY=sk-...
FAL_API_KEY=...
ELEVENLABS_API_KEY=...

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@your-project.iam.gserviceaccount.com
FIREBASE_WEB_API_KEY=AIza...

# PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/database
```

---

## Features

### ✅ Implemented

- 🔐 **Firebase Authentication** - Secure login/signup
- 🗄️ **PostgreSQL Database** - Persistent user data and video metadata
- 📚 **Video Gallery** - User-specific video library with thumbnails
- 🧹 **Session Management** - Automatic cleanup of temp assets
- 💾 **Video Archival** - Permanent storage organized by user
- 🎨 **Thumbnail Generation** - Auto-generated video previews
- ⬇️ **Download Videos** - Download any video from gallery

### 🚀 Usage Flow

1. **Sign Up** - Create account with email/password
2. **Login** - Authenticate to access your workspace
3. **Generate Video** - Enter topic and click generate
4. **View Gallery** - All your videos in sidebar
5. **Download** - Download any video anytime

---

## Troubleshooting

### Firebase Connection Error

```
Error: Could not load Firebase credentials
```

**Solution**: Check that all Firebase environment variables are set correctly in `.env.commercial`

### Database Connection Error

```
Error: could not connect to server
```

**Solution**: 
- Verify `DATABASE_URL` is correct
- For cloud services, check if IP is whitelisted
- For local PostgreSQL, ensure service is running

### Import Error: No module named 'firebase_admin'

```bash
pip install firebase-admin psycopg2-binary opencv-python streamlit
```

### Video Generation Fails

Check that you have credits in your Fal.ai account:
- Login to https://fal.ai/dashboard
- Go to Billing
- Add credits

---

## Project Structure

```
commercial/
├── app.py                    # Main Streamlit application
├── auth.py                   # Firebase authentication
├── database.py               # PostgreSQL operations
├── config.py                 # Configuration management
├── utils/
│   └── session_manager.py    # Session utilities
├── src/                      # Generation pipeline
│   ├── 1_script_gen.py
│   ├── 2_image_gen.py
│   ├── 3_video_gen.py
│   └── 4_audio_gen.py
├── assets/                   # Temporary working directory
└── user_videos/              # Permanent user storage
    └── {firebase_uid}/
        └── {timestamp}/
            ├── FINAL_VIDEO.mp4
            └── thumbnail.png
```

---

## Next Steps

1. **Add Credits**: Top up Fal.ai account for video generation
2. **Test Generation**: Create your first video
3. **Invite Users**: Share the app URL with others
4. **Monitor Usage**: Check PostgreSQL database for user activity

---

## Support

For issues or questions:
1. Check this setup guide
2. Review `.env.commercial` configuration
3. Test Firebase and PostgreSQL connections
4. Check application logs in terminal
