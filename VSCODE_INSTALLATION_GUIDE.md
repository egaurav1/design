# Complete Installation Guide for VS Code

## Step-by-Step Setup

### Prerequisites

- **Python 3.10+**: https://www.python.org/downloads/
- **Git**: https://git-scm.com/
- **VS Code**: https://code.visualstudio.com/
- **FFmpeg**: https://ffmpeg.org/ (installed via package manager)

---

## STEP 1: Clone Project

```bash
# Using Git
git clone https://github.com/yourusername/video-analyzer.git
cd video-analyzer

# Or extract from ZIP
unzip video-analyzer.zip
cd video-analyzer
```

---

## STEP 2: Set Up Virtual Environment

### macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation (should show (venv) in terminal)
which python
# Should output: /path/to/project/venv/bin/python
```

### Windows (PowerShell):

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try again

# Verify activation (should show (venv) in terminal)
```

### Windows (Command Prompt):

```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Verify activation (should show (venv) in terminal)
```

---

## STEP 3: Install FFmpeg

### macOS (Homebrew):

```bash
# Install Homebrew first if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Ubuntu/Debian:

```bash
# Update package manager
sudo apt-get update

# Install FFmpeg
sudo apt-get install -y ffmpeg

# Verify installation
ffmpeg -version
```

### Windows (Chocolatey):

```powershell
# Install Chocolatey first if needed
# Open PowerShell as Administrator, then:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg

# Verify installation
ffmpeg -version
```

### Windows (Manual):

1. Download from: https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\ffmpeg\bin`
   - Click OK
4. Restart command prompt
5. Verify: `ffmpeg -version`

---

## STEP 4: Install Python Dependencies

```bash
# Make sure virtual environment is activated
# On macOS/Linux: source venv/bin/activate
# On Windows: .\venv\Scripts\activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# This takes 5-10 minutes depending on internet speed
# You'll see many packages being downloaded and installed
```

---

## STEP 5: Download Whisper Model

```bash
# This downloads the base Whisper model (~140MB)
# Run this after pip install completes

python -c "import whisper; whisper.load_model('base')"

# Or use a smaller model:
python -c "import whisper; whisper.load_model('tiny')"

# This creates a ~/.cache/whisper directory with the model
```

**Whisper Model Sizes:**

| Model | Size | Speed | Memory | Accuracy |
|-------|------|-------|--------|----------|
| tiny | 75MB | ⚡⚡⚡ | 1GB | 97% |
| base | 140MB | ⚡⚡ | 1.5GB | 97% |
| small | 466MB | ⚡ | 2.7GB | 98% |
| medium | 1.5GB | 🐢 | 5.3GB | 99% |
| large | 2.9GB | 🐢🐢 | 10GB | 99% |

Start with `base` or `tiny`. Upgrade if needed for accuracy.

---

## STEP 6: Set Up Environment Variables

### Create `.env` File:

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings
# (Use VS Code to edit)
```

### Minimal `.env` (Free Setup):

```
USE_LOCAL_OLLAMA=false
WHISPER_MODEL=base
LOG_LEVEL=INFO
ENABLE_FRAME_EXTRACTION=true
ENABLE_VISUAL_ANALYSIS=false
ENABLE_TRANSCRIPTION=true
ENABLE_SUMMARIZATION=false
```

This gives you working transcription with NO API keys needed!

---

## STEP 7: Configure VS Code

### 1. Open Folder in VS Code

```bash
# In the project directory, open VS Code
code .
```

Or:
1. Open VS Code
2. File → Open Folder
3. Select the `video-analyzer` directory

### 2. Select Python Interpreter

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type: "Python: Select Interpreter"
3. Choose the one that says `./venv/bin/python` or similar

### 3. Install VS Code Extensions

1. Open Extensions sidebar (Ctrl+Shift+X)
2. Install:
   - **Python** (ms-python.python)
   - **Pylance** (ms-python.vscode-pylance)
   - **Black Formatter** (ms-python.black-formatter)
   - **Jupyter** (ms-toolsai.jupyter) - optional

### 4. Create Launch Configuration

1. Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "args": ["analyze", "sample.mp4"],
            "justMyCode": true
        },
        {
            "name": "Python: Test",
            "type": "python",
            "request": "launch",
            "program": "-m",
            "args": ["pytest", "tests/"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## STEP 8: Test Installation

### Test 1: Check Python Setup

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate   # Windows

# Check Python version
python --version
# Should show: Python 3.10+ or higher

# Check virtual environment is active
which python  # macOS/Linux shows venv path
# or
where python  # Windows shows venv path
```

### Test 2: Check Dependencies

```bash
python -c "import whisper; print('✅ Whisper OK')"
python -c "import cv2; print('✅ OpenCV OK')"
python -c "import ffmpeg; print('✅ FFmpeg-python OK')"
python -c "from langgraph.graph import StateGraph; print('✅ LangGraph OK')"
```

### Test 3: Check Configuration

```bash
python src/main.py config
```

Should output your configuration without errors.

### Test 4: Test Whisper

```bash
python src/main.py test --transcribe
```

Should load Whisper model.

---

## STEP 9: Run Your First Analysis

### 1. Download Sample Video

```bash
# Create uploads directory
mkdir -p uploads

# Download a sample video (or use your own)
# Or use ffmpeg to create a short test video
ffmpeg -f lavfi -i testsrc=duration=10:size=320x240:rate=1 -f lavfi -i sine=frequency=1000:duration=10 test.mp4
```

### 2. Run Analysis

```bash
# Activate venv first!
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate   # Windows

# Run analysis
python src/main.py analyze uploads/test.mp4

# Or from VS Code:
# 1. Press F5 to run the launch config
# 2. Or use Ctrl+Shift+D and click Run
```

### 3. View Results

```bash
# Results saved to:
cat outputs/test/transcript.txt
cat outputs/test/metadata.json
```

---

## Common Issues & Solutions

### ❌ "python: command not found" on macOS

```bash
# Python isn't in PATH
# Use python3 instead:
python3 -m venv venv
source venv/bin/activate
python3 --version

# Or install using Homebrew:
brew install python@3.11
```

### ❌ "venv: command not found"

```bash
# On macOS, python might not have venv
# Install it:
brew install python@3.11

# Or use apt on Linux:
sudo apt-get install python3-venv
```

### ❌ "FFmpeg not found"

```bash
# Check installation
ffmpeg -version

# If not installed, see STEP 3 above

# If installed but not in PATH:
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
# Windows: add to PATH (see STEP 3)
```

### ❌ "ModuleNotFoundError" when running code

```bash
# Make sure venv is activated:
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows

# Then reinstall dependencies:
pip install -r requirements.txt
```

### ❌ "whisper module not found"

```bash
# Make sure venv is activated

# Reinstall openai-whisper:
pip install --upgrade openai-whisper

# Download the model:
python -c "import whisper; whisper.load_model('base')"
```

### ❌ Whisper model very slow

```bash
# Use smaller model - edit .env:
WHISPER_MODEL=tiny

# Then test:
python -c "import whisper; whisper.load_model('tiny')"
```

### ❌ "No module named 'torch'"

```bash
# Torch is required for Whisper
# Reinstall it:
pip install torch torchvision torchaudio

# If you have GPU (CUDA), install GPU version:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### ❌ Python crashes with memory error

```bash
# Use smaller Whisper model:
WHISPER_MODEL=tiny

# Or disable features in .env:
ENABLE_FRAME_EXTRACTION=false
ENABLE_VISUAL_ANALYSIS=false

# Or use CPU only:
export CUDA_VISIBLE_DEVICES=""  # macOS/Linux
set CUDA_VISIBLE_DEVICES=       # Windows
```

### ❌ Video file not found error

```bash
# Make sure:
1. File exists in current directory or use full path
2. Filename has no spaces (or quote it)
3. File format is supported (mp4, webm, mov, avi)

# Test with:
ls -la uploads/  # macOS/Linux
dir uploads      # Windows
```

---

## File Structure After Setup

```
video-analyzer/
├── venv/                  # Virtual environment (created)
├── src/                   # Source code
│   ├── main.py
│   ├── config.py
│   ├── logger.py
│   ├── models.py
│   ├── graph/
│   │   └── workflow.py
│   ├── transcription/
│   │   └── whisper_local.py
│   └── llm/
│       └── llm_interface.py
├── uploads/              # Your video files
├── outputs/              # Results (created after first run)
├── logs/                 # Log files (created)
├── temp/                 # Temporary files (created)
├── tests/               # Test files
├── requirements.txt
├── .env                 # Your settings (created from .env.example)
├── .env.example
└── README.md
```

---

## Next Steps

1. ✅ Create a sample video or use an existing one
2. ✅ Place it in the `uploads/` directory
3. ✅ Run: `python src/main.py analyze uploads/video.mp4`
4. ✅ Check results in `outputs/` directory

---

## Running with VS Code

### Method 1: Terminal (Easiest)

```bash
# Open Terminal in VS Code (Ctrl+`)
python src/main.py analyze uploads/video.mp4
```

### Method 2: Run Button

```
1. Open src/main.py in editor
2. Click "Run" button (top right)
3. Or press Ctrl+F5
```

### Method 3: Debug Mode

```
1. Press F5 to start debugging
2. Choose "Python: Main" config
3. Set breakpoints by clicking line numbers
4. Step through code
```

---

## Tips

- **Keep VS Code terminal open**: Shows logs and progress
- **Use .gitignore**: Don't commit venv/ or outputs/
- **Enable auto-save**: VS Code → File → Auto Save
- **Use Python formatter**: Right-click → Format Document

---

## Still Having Issues?

1. Check logs: `cat logs/video_analyzer.log`
2. Run tests: `python src/main.py test`
3. Check config: `python src/main.py config`
4. Try sample video first (see STEP 9)
5. Post issue on GitHub with error message

---

Good luck! 🚀 You should now have a working video analyzer in VS Code!
