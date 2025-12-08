# 🔧 Troubleshooting Guide

Complete solutions for common issues when setting up and running the OmniComni pipeline.

---

## 🔥 Critical Issues

### 1. Model Access Denied (403 Forbidden)

**Symptoms:**
```
403 Client Error: Forbidden
HTTPError: 403 Client Error: Forbidden for url
Repository not found or you don't have access
```

**Root Cause:** Llama models are gated and require explicit access approval.

**Solution:**

1. **Request Access:**
   - Visit: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
   - Click the "Request Access" button
   - Fill out the form (basic info only)
   - Accept Meta's license agreement
   
2. **Wait for Approval:**
   - Usually instant to a few hours
   - Check your email for confirmation
   
3. **Re-authenticate:**
   ```bash
   huggingface-cli logout
   huggingface-cli login
   ```

4. **Verify Access:**
   ```bash
   huggingface-cli whoami
   ```

**Still not working?**
- Try a different browser to request access
- Use your actual HuggingFace account (not company/organization)
- Check if you're logged into the correct account

---

### 2. Out of Memory (OOM) Errors

**Symptoms:**
```
CUDA out of memory
RuntimeError: CUDA error: out of memory
torch.cuda.OutOfMemoryError
```

**Solutions (in order of preference):**

#### A. **Close Other GPU Applications**

```bash
# Check what's using GPU
nvidia-smi

# Kill process using GPU (find PID from nvidia-smi)
kill -9 <PID>  # Linux
taskkill /PID <PID> /F  # Windows
```

#### B. **Use 8-bit Instead of 4-bit**

Edit `src/scene_generator.py` (around line 24):

**Change from:**
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,  # ← Change this
    bnb_4bit_compute_dtype=torch.float16,
    ...
)
```

**To:**
```python
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,  # ← 8-bit uses less VRAM
    ...
)
```

#### C. **Enable CPU Offload**

Add to model loading (in `scene_generator.py`):

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto",
    max_memory={0: "10GB", "cpu": "30GB"},  # ← Add this
    offload_folder="offload",  # ← And this
    torch_dtype=torch.float16
)
```

#### D. **Reduce max_new_tokens**

Edit `config.py`:

```python
MAX_NEW_TOKENS = 800  # ← Reduce from 1200
```

#### E. **Use Smaller Model**

Edit `src/scene_generator.py` (line 12):

```python
# Change from:
DEFAULT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

# To:
DEFAULT_MODEL = "meta-llama/Llama-3.2-1B-Instruct"  # Smaller model
```

---

### 3. Windows DLL Errors (bitsandbytes)

**Symptoms:**
```
DLL load failed while importing
OSError: [WinError 126] The specified module could not be found
ImportError: cannot import name 'xxx' from bitsandbytes
```

**Root Cause:** Standard `bitsandbytes` doesn't support Windows natively.

**Solutions:**

#### Solution 1: Use Windows-Compatible Wheel (Recommended)

```powershell
# Uninstall current version
pip uninstall bitsandbytes -y

# Install Windows version
pip install bitsandbytes-windows
```

#### Solution 2: Use Pre-Compiled Wheel

```powershell
pip uninstall bitsandbytes -y
pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl
```

#### Solution 3: Install Visual C++ Redistributable

1. Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Run installer
3. Restart computer
4. Retry: `pip install bitsandbytes-windows`

#### Solution 4: Disable Quantization (Fallback)

Edit `config.py`:

```python
USE_4BIT_QUANTIZATION = False  # Disable quantization
```

**⚠️ Warning:** This will use more VRAM (~12GB instead of ~4GB)

---

## ⚠️ Common Issues

### 4. CUDA Not Detected

**Symptom:**
```python
torch.cuda.is_available()  # Returns False
```

**Solutions:**

#### Check NVIDIA Driver

```bash
nvidia-smi
```

If command not found:

**Linux:**
```bash
sudo apt update
sudo apt install nvidia-driver-535
sudo reboot
```

**Windows:**
- Download drivers: https://www.nvidia.com/download/index.aspx
- Restart after install

#### Check PyTorch CUDA Version

```python
import torch
print(torch.__version__)  # Should show +cu118 or +cu121
```

If it shows `+cpu`:

```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio -y

# Install CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Match CUDA Toolkit Version

```bash
# Check installed CUDA
nvcc --version

# If 11.8, use:
pip install torch --index-url https://download.pytorch.org/whl/cu118

# If 12.1, use:
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

---

### 5. Slow Generation (CPU Instead of GPU)

**Symptom:** Model loads but generation takes 5+ minutes per scene.

**Diagnosis:**

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Model device: {next(model.parameters()).device}")
```

If device shows `cpu` but CUDA is available:

**Solution:**

Edit `src/scene_generator.py`, add explicit device:

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map={"": 0},  # ← Force GPU 0
    torch_dtype=torch.float16
)
```

---

### 6. Import Errors

#### transformers

```bash
pip install --upgrade transformers>=4.57.0
```

#### accelerate

```bash
pip install accelerate>=0.24.0
```

#### edge-tts

```bash
pip install edge-tts>=6.1.0
```

#### "No module named 'src'"

You're in the wrong directory. Run from project root:

```bash
cd c:\Users\grish\OneDrive\Desktop\omnicomnimodel
python main.py "Your topic"
```

---

### 7. JSON Parsing Errors

**Symptom:**
```
JSON parsing error: Expecting value: line X column Y
Using fallback scenes
```

**Cause:** Model generated text but not valid JSON.

**Solutions:**

#### A. Use Verbose Mode

```bash
python main.py "Your topic" --verbose
```

This shows what the model actually generated.

#### B. Adjust Temperature

Edit `config.py`:

```python
TEMPERATURE = 0.5  # Lower = more focused, better JSON (was 0.7)
```

#### C. Use Instruct Model

Ensure using `-Instruct` model version:

```python
DEFAULT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"  # ← Must have -Instruct
```

---

### 8. edge-tts Connection Errors

**Symptom:**
```
aiohttp.ClientError
Connection refused
edge-tts unable to connect
```

**Solutions:**

#### Check Internet Connection

```bash
ping 8.8.8.8
```

#### Try Different Voice

Edit `src/audio_generator.py`:

```python
VOICE_MAP = {
    "neutral": "en-US-AriaNeural",  # Try different voice
    ...
}
```

#### Test edge-tts Directly

```bash
edge-tts --text "Test" --voice en-US-ChristopherNeural --write-media test.mp3
```

---

## 🐛 Advanced Debugging

### Enable Detailed Logging

Create `debug.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your code
from src.scene_generator import SceneGenerator
# ...
```

### Check Model Loading Step-by-Step

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 1. Check CUDA
print(f"CUDA: {torch.cuda.is_available()}")

# 2. Load tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
    print("✅ Tokenizer loaded")
except Exception as e:
    print(f"❌ Tokenizer error: {e}")

# 3. Load model (CPU, no quantization)
try:
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.2-3B-Instruct",
        torch_dtype=torch.float32
    )
    print("✅ Model loaded")
except Exception as e:
    print(f"❌ Model error: {e}")
```

### Monitor VRAM in Real-Time

**Terminal 1:**
```bash
python main.py "Your topic"
```

**Terminal 2:**
```bash
watch -n 0.5 nvidia-smi  # Linux
# Or PowerShell:
while($true) { nvidia-smi; Start-Sleep -Seconds 0.5 }
```

---

## 📞 Still Stuck?

### Check System Info

Run this diagnostic script:

```python
import torch
import transformers
import sys
import platform

print("="*50)
print("SYSTEM DIAGNOSTIC")
print("="*50)
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"Transformers: {transformers.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

Save output and share when asking for help.

---

## 🆘 Emergency Fallback: Run on CPU

If nothing works:

1. **Disable quantization:**
   ```python
   # In config.py
   USE_4BIT_QUANTIZATION = False
   ```

2. **Use smaller model:**
   ```python
   # In config.py
   DEFAULT_MODEL = "meta-llama/Llama-3.2-1B-Instruct"
   ```

3. **Run:**
   ```bash
   python main.py "Short topic" --scenes 3
   ```

4. **Be patient:** CPU inference is 10-100x slower.

---

## ✅ Prevention Checklist

Before starting:

- [ ] Fresh environment (conda or venv)
- [ ] PyTorch with CUDA explicitly installed
- [ ] Windows users: bitsandbytes-windows
- [ ] HuggingFace authenticated
- [ ] Model access approved
- [ ] Run `test_llama.py` first
- [ ] Monitor with `nvidia-smi`

---

**Most issues are solved by:**
1. Fresh environment
2. Correct PyTorch CUDA installation
3. Windows bitsandbytes wheel
4. HuggingFace model access approval

