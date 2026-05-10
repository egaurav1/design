# Video Analysis Project - VS Code Setup Guide

## Project Structure

```
video-analyzer/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── logger.py              # Logging setup
│   ├── models.py              # Data models
│   ├── video_processor/
│   │   ├── __init__.py
│   │   ├── audio_extractor.py # Extract audio from video
│   │   ├── frame_extractor.py # Extract key frames
│   │   └── utils.py           # Video utilities
│   ├── transcription/
│   │   ├── __init__.py
│   │   ├── whisper_local.py   # Local Whisper (offline)
│   │   ├── groq_whisper.py    # Groq API (free alternative)
│   │   └── transcriber.py     # Base transcriber
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── ollama_client.py   # Ollama (local LLM)
│   │   ├── anthropic_client.py # Claude (with API key)
│   │   └── llm_interface.py   # Abstract interface
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── workflow.py        # LangGraph workflow
│   │   └── nodes.py           # Graph nodes
│   └── main.py                # Entry point
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── .env.example
├── README.md
└── setup.sh
```

## Installation & Setup

### 1. Clone/Create Project

```bash
mkdir video-analyzer
cd video-analyzer
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Copy requirements below to requirements.txt, then:
pip install -r requirements.txt

# Also install ffmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

### 4. Set Up Environment Variables

Create `.env` file:

```
# API Keys (optional - leave blank if using local models)
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=...

# Model Settings
USE_LOCAL_OLLAMA=true        # Use Ollama for local inference
OLLAMA_MODEL=mistral:7b      # Local model name
WHISPER_MODEL=base           # Local Whisper model size

# Processing
VIDEO_UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp
LOG_LEVEL=INFO
```

### 5. Copy `.env.example` to `.env`

```bash
cp .env.example .env
# Edit .env with your settings
```

---

## Required Files

### `requirements.txt`

```
# Core dependencies
python-dotenv==1.0.0
pydantic==2.4.2

# LangGraph & LangChain (orchestration)
langgraph==0.0.32
langchain==0.1.0
langchain-anthropic==0.0.15
langchain-community==0.0.17

# Video Processing
opencv-python==4.8.1.78
ffmpeg-python==0.2.1
moviepy==1.0.3
Pillow==10.1.0

# Transcription (Local)
openai-whisper==20231117
torch==2.1.0

# LLM (Local)
ollama-python==0.0.11
requests==2.31.0

# LLM (Cloud alternatives)
groq==0.4.1
anthropic==0.7.1

# Utilities
numpy==1.24.3
pydantic-settings==2.0.3
tqdm==4.66.1

# Development
pytest==7.4.3
python-dotenv==1.0.0
```

### Setup Script (`setup.sh`)

```bash
#!/bin/bash

echo "🚀 Setting up Video Analyzer Project..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p uploads outputs temp logs

# Create .env file
echo "⚙️  Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env created. Please edit with your API keys."
else
    echo "✅ .env already exists."
fi

# Download Whisper model (optional)
read -p "Download Whisper model? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎙️  Downloading Whisper model..."
    python -c "import whisper; whisper.load_model('base')"
fi

echo "✅ Setup complete!"
echo "Run: source venv/bin/activate"
echo "Then: python src/main.py"
```

---

## VS Code Configuration

### `.vscode/settings.json`

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/temp": true
    }
}
```

### `.vscode/launch.json`

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

## LangGraph Setup

LangGraph is perfect for multi-step workflows. Here's the structure:

### Nodes in LangGraph:

1. **Input Node** → Load video
2. **Extract Audio Node** → ffmpeg
3. **Transcribe Node** → Whisper (local)
4. **Extract Frames Node** → OpenCV
5. **Analyze Frames Node** → Local LLM
6. **Summarize Node** → Local LLM or Claude
7. **Output Node** → Save results

### Graph Flow:

```
Input Video
    ↓
Extract Audio
    ↓
Transcribe (Whisper)
    ├→ Extract Frames
    │   ↓
    │  Analyze Frames
    │   ↓
    └→ Summarize
        ↓
    Output Results
```

---

## Minimal Working Example

To test your setup, run:

```bash
cd video-analyzer
source venv/bin/activate
python src/main.py --help
```

This will show available commands without errors.

---

## Next Steps

1. **Download Whisper model**: Takes 1-2 minutes
   ```bash
   python -c "import whisper; whisper.load_model('base')"
   ```

2. **(Optional) Set up Ollama for local LLM**:
   - Download: https://ollama.ai
   - Run: `ollama pull mistral:7b`
   - Test: `ollama run mistral:7b "Hello"`

3. **Test with a sample video**:
   ```bash
   python src/main.py upload --video sample.mp4
   ```

4. **View logs**:
   ```bash
   tail -f logs/app.log
   ```

---

## Environment Variables Explained

| Variable | Default | Options | Purpose |
|----------|---------|---------|---------|
| `USE_LOCAL_OLLAMA` | true | true/false | Use local LLM vs API |
| `OLLAMA_MODEL` | mistral:7b | mistral, llama2, neural-chat | Which local model |
| `WHISPER_MODEL` | base | tiny, base, small, medium, large | Model size/accuracy |
| `ANTHROPIC_API_KEY` | (empty) | Your API key | Claude API access |
| `GROQ_API_KEY` | (empty) | Your API key | Groq free API |
| `LOG_LEVEL` | INFO | DEBUG, INFO, WARNING, ERROR | Logging verbosity |

---

## Troubleshooting Setup

### "Command not found: ffmpeg"
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
# Or download from: https://ffmpeg.org/download.html
```

### "ModuleNotFoundError: No module named 'torch'"
```bash
# Reinstall torch (handles GPU properly)
pip install torch torchvision torchaudio
```

### "CUDA out of memory" with Whisper
```bash
# Use smaller model
WHISPER_MODEL=tiny  # Fast, less accurate
# Or CPU only:
CUDA_VISIBLE_DEVICES="" python src/main.py
```

### "ollama: command not found"
- Download from https://ollama.ai
- Make sure it's in PATH
- Or use API keys with Groq/Anthropic instead

---

## VS Code Extensions Recommended

Install in VS Code:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Jupyter (ms-toolsai.jupyter)
- Thunder Client (REST client)

---

## Running the Project

### From Terminal:
```bash
source venv/bin/activate
python src/main.py --help
```

### From VS Code:
1. Open folder in VS Code
2. Click "Run and Debug" (Ctrl+Shift+D)
3. Select "Python: Main"
4. Press F5 to start

### With Docker (optional):
See Dockerfile section later

---

## Project Ready!

You now have a complete structure. The next part will have all the actual code files.

Ready to move to the code implementation? ✅
