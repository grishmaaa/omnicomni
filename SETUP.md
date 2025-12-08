# 🚀 Professional Environment Setup Guide

Complete setup guide for the OmniComni Audio Scene Generator with solutions for common edge cases.

---

## 📋 System Requirements

- **OS**: Windows 10/11 or Linux (Ubuntu 20.04+)
- **GPU**: NVIDIA RTX series with 8-12GB VRAM (recommended)
- **Python**: 3.10 or 3.11 (3.12 has limited library support)
- **Storage**: ~10GB for models and dependencies

---

## 1️⃣ Environment & Dependency Setup

### Option A: Conda (Recommended)

#### **Linux/MacOS**

```bash
# Create fresh environment
conda create -n video_pipeline python=3.10 -y
conda activate video_pipeline

# Install PyTorch with CUDA 11.8
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

# Or for CUDA 12.1
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install other dependencies
pip install transformers accelerate bitsandbytes edge-tts scipy huggingface_hub
```

#### **Windows**

```powershell
# Create fresh environment
conda create -n video_pipeline python=3.10 -y
conda activate video_pipeline

# Install PyTorch with CUDA 11.8
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

# CRITICAL: Use Windows-compatible bitsandbytes
pip install bitsandbytes-windows

# Install other dependencies
pip install transformers accelerate edge-tts scipy huggingface_hub
```

**⚠️ Windows Edge Case**: If `bitsandbytes-windows` fails, try:
```powershell
pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl
```

### Option B: pip + venv

#### **Linux/MacOS**

```bash
# Create virtual environment
python3.10 -m venv video_pipeline
source video_pipeline/bin/activate

# Install PyTorch with CUDA 11.8 (CRITICAL: Specify CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or for CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install dependencies from requirements
pip install -r requirements.txt
```

#### **Windows**

```powershell
# Create virtual environment
python -m venv video_pipeline
.\video_pipeline\Scripts\activate

# Install PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Windows-compatible bitsandbytes
pip install bitsandbytes-windows

# Install other dependencies
pip install transformers accelerate edge-tts scipy huggingface_hub
```

---

## 2️⃣ Verify Installation

### Quick Check Script

```python
# verify_setup.py
import torch
import transformers
import bitsandbytes
import edge_tts

print("✅ All imports successful!")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

**Run it:**
```bash
python verify_setup.py
```

**Expected Output:**
```
✅ All imports successful!
PyTorch version: 2.3.0+cu118
CUDA available: True
CUDA version: 11.8
GPU: NVIDIA GeForce RTX 3080
VRAM: 10.00 GB
```

---

## 3️⃣ HuggingFace Authentication

### Method 1: CLI (Recommended)

```bash
# Install CLI
pip install huggingface_hub

# Login
huggingface-cli login
```

**When prompted**, paste your token from: https://huggingface.co/settings/tokens

### Method 2: Environment Variable

```bash
# Linux/MacOS
export HF_TOKEN="hf_your_token_here"

# Windows PowerShell
$env:HF_TOKEN="hf_your_token_here"

# Windows CMD
set HF_TOKEN=hf_your_token_here
```

### Method 3: Code (Not Recommended)

```python
from huggingface_hub import login
login(token="hf_your_token_here")
```

### ⚠️ Request Model Access

**CRITICAL**: Llama models are gated. You MUST request access:

1. Visit: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
2. Click "Request Access"
3. Accept the license agreement
4. Wait for approval (usually instant to a few hours)

---

## 4️⃣ Run Test Script

```bash
python test_llama.py
```

This will:
- ✅ Check authentication
- ✅ Detect GPU/CPU
- ✅ Load model with appropriate quantization
- ✅ Run test inference
- ✅ Report VRAM usage

---

## 5️⃣ Platform-Specific Notes

### **Windows**

#### bitsandbytes Issues

**Symptom**: `DLL load failed` or `OSError: [WinError 126]`

**Solutions** (try in order):

1. **Install Visual C++ Redistributable**:
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install and restart

2. **Use pre-compiled wheel**:
   ```powershell
   pip uninstall bitsandbytes
   pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl
   ```

3. **Disable quantization** (fallback):
   - Edit `config.py`: Set `USE_4BIT_QUANTIZATION = False`

#### CUDA Path

Ensure CUDA is in PATH:
```powershell
nvcc --version
```

If not found:
```powershell
$env:PATH += ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin"
```

### **Linux**

#### CUDA Drivers

```bash
# Check NVIDIA driver
nvidia-smi

# If not found, install
sudo apt update
sudo apt install nvidia-driver-535 nvidia-cuda-toolkit
```

#### gcc/g++ Version

bitsandbytes requires gcc 7.0+:
```bash
gcc --version

# If too old
sudo apt install gcc-9 g++-9
export CC=gcc-9
export CXX=g++-9
```

---

## 6️⃣ VRAM Monitoring

### Real-Time Monitoring

**Linux/Windows**:
```bash
# Terminal 1: Run your script
python main.py "Your topic"

# Terminal 2: Monitor VRAM
watch -n 1 nvidia-smi
```

**Or use**:
```bash
nvidia-smi --query-gpu=memory.used,memory.total --format=csv -l 1
```

### In Python

```python
import torch

def print_gpu_memory():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1e9
        reserved = torch.cuda.memory_reserved(0) / 1e9
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU Memory: {allocated:.2f}GB used, {reserved:.2f}GB reserved, {total:.2f}GB total")

print_gpu_memory()
```

---

## 7️⃣ Conda Environment.yml (Alternative)

Save as `environment.yml`:

```yaml
name: video_pipeline
channels:
  - pytorch
  - nvidia
  - conda-forge
dependencies:
  - python=3.10
  - pytorch::pytorch
  - pytorch::torchvision
  - pytorch::torchaudio
  - pytorch::pytorch-cuda=11.8
  - pip
  - pip:
    - transformers>=4.57.0
    - accelerate>=0.24.0
    - bitsandbytes>=0.41.0  # Use bitsandbytes-windows on Windows
    - edge-tts>=6.1.0
    - scipy
    - huggingface_hub
```

**Create environment**:
```bash
conda env create -f environment.yml
conda activate video_pipeline
```

---

## 8️⃣ Docker (Advanced)

For a completely isolated environment:

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3.10 python3-pip git

WORKDIR /app

COPY requirements.txt .
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**Build & Run**:
```bash
docker build -t omnicomni .
docker run --gpus all omnicomni "Your topic"
```

---

## 🎯 Quick Start Checklist

- [ ] Install Conda/Python 3.10
- [ ] Create environment
- [ ] Install PyTorch **with CUDA** (use specific commands above)
- [ ] Install dependencies (bitsandbytes-windows on Windows)
- [ ] Run `verify_setup.py`
- [ ] Authenticate with HuggingFace
- [ ] Request Llama model access
- [ ] Run `test_llama.py`
- [ ] Monitor with `nvidia-smi`

---

## 📞 Still Having Issues?

See `TROUBLESHOOTING.md` for detailed solutions to common problems.
