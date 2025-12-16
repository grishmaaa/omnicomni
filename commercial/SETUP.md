# 🚀 AI Video Generator - Setup Guide

**Production-ready environment setup for Windows, Mac, and Linux**

---

## 📋 Prerequisites

- **Python 3.10+** installed
- **Git** installed
- **FFmpeg** installed (for video processing)

**Check your Python version:**
```bash
python --version
# Should show: Python 3.10.x or higher
```

---

## 🔧 Step 1: Clone Repository

```bash
git clone https://github.com/your-org/ai-video-generator.git
cd ai-video-generator
```

---

## 🐍 Step 2: Create Virtual Environment

### **Windows (PowerShell)**

```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Windows (Command Prompt)**

```cmd
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate.bat
```

### **Mac / Linux (Bash/Zsh)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

**Verify activation:**
Your terminal prompt should now show `(venv)` at the beginning.

---

## 📦 Step 3: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements-production.txt

# Verify installation
pip list
```

**Expected output:**
```
groq                 0.4.x
fal-client           0.4.x
elevenlabs           0.2.x
moviepy              1.0.x
pydantic             2.x.x
...
```

---

## 🔐 Step 4: Configure Environment Variables

### **Create .env file**

```bash
# Copy the template
cp .env.production.example .env

# Windows (PowerShell)
Copy-Item .env.production.example .env

# Windows (Command Prompt)
copy .env.production.example .env
```

### **Add your API keys**

Open `.env` in your text editor and replace placeholders:

```bash
# Required API Keys
GROQ_API_KEY=gsk_your_actual_groq_key_here
FAL_API_KEY=your_actual_fal_key_here
ELEVENLABS_API_KEY=your_actual_elevenlabs_key_here
```

**Where to get API keys:**

| Service | URL | Free Tier |
|---------|-----|-----------|
| **Groq** | https://console.groq.com/keys | ✅ Yes |
| **Fal.ai** | https://fal.ai/dashboard/keys | ✅ Yes ($1 credit) |
| **ElevenLabs** | https://elevenlabs.io/app/settings/api-keys | ✅ Yes (10k chars/month) |

---

## ✅ Step 5: Verify Setup

### **Test imports**

```bash
python -c "import groq, fal_client, elevenlabs, moviepy; print('✅ All imports successful!')"
```

### **Test environment loading**

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Environment loaded')"
```

### **Check API keys**

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Groq:', 'SET' if os.getenv('GROQ_API_KEY') else 'MISSING')"
```

---

## 🎬 Step 6: Run the Application

```bash
# Run the main application
python app.py

# Or run individual scripts
python src/1_script_gen.py
python src/2_image_gen.py
python src/3_video_gen.py
python src/4_audio_gen.py
python src/5_editor.py
```

---

## 🛠️ Troubleshooting

### **"ModuleNotFoundError: No module named 'X'"**

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements-production.txt
```

### **"API key not found" or "401 Unauthorized"**

**Solution:**
1. Check `.env` file exists in project root
2. Verify API keys are correct (no extra spaces)
3. Ensure keys start with correct prefixes:
   - Groq: `gsk_`
   - Fal.ai: varies
   - ElevenLabs: varies

### **FFmpeg not found**

**Windows:**
```powershell
# Install via Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**Mac:**
```bash
# Install via Homebrew
brew install ffmpeg
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### **Virtual environment not activating**

**Windows PowerShell:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\Activate.ps1
```

---

## 📁 Directory Structure

After setup, your project should look like this:

```
ai-video-generator/
├── venv/                    # Virtual environment (gitignored)
├── assets/                  # Generated files (gitignored)
│   ├── images/
│   ├── videos/
│   └── audio/
├── src/
│   ├── 1_script_gen.py
│   ├── 2_image_gen.py
│   ├── 3_video_gen.py
│   ├── 4_audio_gen.py
│   └── 5_editor.py
├── app.py
├── requirements-production.txt
├── .env                     # Your secrets (gitignored)
├── .env.production.example  # Template (committed)
├── .gitignore
└── SETUP.md                 # This file
```

---

## 🔄 Daily Workflow

### **Starting work**

```bash
# Navigate to project
cd ai-video-generator

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
.\venv\Scripts\Activate.ps1  # Windows

# Pull latest changes
git pull
```

### **Ending work**

```bash
# Deactivate virtual environment
deactivate

# Commit your changes (never commit .env!)
git add .
git commit -m "Your commit message"
git push
```

---

## 🔐 Security Checklist

Before committing code, verify:

- [ ] `.env` is in `.gitignore`
- [ ] No API keys in source code
- [ ] No API keys in commit history
- [ ] `assets/` folder is gitignored
- [ ] `.env.production.example` has no real keys

**Check for leaked secrets:**
```bash
# Search for potential API keys in tracked files
git grep -i "api_key"
git grep -i "secret"
```

---

## 📊 Cost Monitoring

**Estimated costs per video:**
- Groq (Script): ~$0.002
- Fal.ai (Images): ~$0.15
- Fal.ai (Video): ~$0.50
- ElevenLabs (Audio): ~$0.15
- **Total:** ~$0.82/video

**Set budget alerts in `.env`:**
```bash
MAX_COST_PER_VIDEO=2.00
MONTHLY_BUDGET=100.00
```

---

## 🆘 Getting Help

1. **Check logs:** Look for error messages in terminal
2. **Verify API keys:** Ensure all three are set correctly
3. **Check credits:** Verify you have credits on each platform
4. **Review docs:** Check API provider documentation

---

## 🎓 Next Steps

1. ✅ Complete this setup
2. 📖 Read the main README.md
3. 🧪 Run a test generation
4. 📊 Monitor costs
5. 🚀 Start creating videos!

**Setup complete!** You're ready to generate AI videos. 🎬
