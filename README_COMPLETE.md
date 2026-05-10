# 🎬 Video Analyzer - LangGraph Edition

AI-powered video analysis tool using **LangGraph**, **open-source LLMs**, and **local Whisper transcription**.

## Features

✨ **Complete Workflow:**
- 🎬 **Video Processing** - Extract audio & frames using FFmpeg + OpenCV
- 🗣️ **Transcription** - Local Whisper model (no API needed)
- 🔍 **Visual Analysis** - Analyze frames with LLM
- ✍️ **Summarization** - Generate summaries of different lengths
- 💾 **Results Export** - Save transcript, summary, metadata

⚡ **Tech Stack:**
- **LangGraph** - Workflow orchestration
- **Whisper** - Speech-to-text (local)
- **Ollama** - Local LLM (optional)
- **Claude** - Cloud LLM (optional)
- **FFmpeg** - Video processing
- **OpenCV** - Frame extraction

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/video-analyzer.git
cd video-analyzer
chmod +x setup.sh
./setup.sh
```

### 2. Download Whisper Model

```bash
python -c "import whisper; whisper.load_model('base')"
```

This downloads the Whisper model (~140MB). Sizes:
- `tiny` - Fastest, least accurate
- `base` - Good balance (recommended)
- `small` - More accurate, slower
- `medium` - High accuracy, slower
- `large` - Best accuracy, slowest

### 3. (Optional) Set Up Ollama for Local LLM

```bash
# Download Ollama: https://ollama.ai
# In another terminal:
ollama serve

# Download a model (in main terminal):
ollama pull mistral:7b
```

### 4. Run Analysis

```bash
source venv/bin/activate

# Analyze a video
python src/main.py analyze video.mp4

# See options
python src/main.py analyze --help

# Test components
python src/main.py test

# View configuration
python src/main.py config
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# LLM Settings (local is free, no API needed)
USE_LOCAL_OLLAMA=true              # Use local model or API
OLLAMA_MODEL=mistral:7b            # Local model to use
OLLAMA_BASE_URL=http://localhost:11434

# For cloud LLMs (optional)
ANTHROPIC_API_KEY=sk-ant-...       # Claude API key
GROQ_API_KEY=...                   # Groq API key (free tier)

# Whisper Settings
WHISPER_MODEL=base                 # tiny, base, small, medium, large

# Processing
FRAMES_PER_MINUTE=2                # How many frames to extract
MAX_VIDEO_SIZE_MB=500              # Maximum video size
SUPPORTED_FORMATS=mp4,webm,mov,avi,mkv

# Logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR

# Feature Flags (disable to skip steps)
ENABLE_FRAME_EXTRACTION=true
ENABLE_VISUAL_ANALYSIS=true
ENABLE_TRANSCRIPTION=true
ENABLE_SUMMARIZATION=true
```

---

## Usage Examples

### Basic Analysis

```bash
# Analyze video with all features
python src/main.py analyze video.mp4

# Analyze without frame extraction (faster)
python src/main.py analyze video.mp4 --skip-frames

# Analyze transcription only
python src/main.py analyze video.mp4 --skip-frames --skip-visual --skip-summary
```

### In Python Code

```python
from src.main import analyze_video

result = analyze_video(
    "path/to/video.mp4",
    transcribe=True,
    summarize=True
)

print(result["summary"]["medium_summary"])
print(f"Words: {len(result['transcription']['text'].split())}")
```

### Using LangGraph Directly

```python
from src.graph.workflow import create_workflow
from src.models import GraphState

# Create workflow
app = create_workflow()

# Create state
state = GraphState(video_path="video.mp4")

# Run workflow
final_state = app.invoke(state)

# Access results
print(final_state.summary)
print(final_state.transcription)
```

---

## Architecture

### LangGraph Workflow

```
Input Video
    ↓
[Validate Input]
    ↓
[Extract Metadata]  ← ffprobe
    ↓
[Extract Audio]     ← ffmpeg
    ↓
[Transcribe]        ← Whisper (local)
    ↓
[Extract Frames]    ← OpenCV
    ↓
[Analyze Frames]    ← LLM (Ollama/Claude)
    ↓
[Summarize]         ← LLM (Ollama/Claude)
    ↓
[Save Results]      ← JSON/TXT files
    ↓
[Cleanup Temp]      ← Remove temp files
    ↓
[Finalize]
    ↓
Output Results
```

### Project Structure

```
video-analyzer/
├── src/
│   ├── config.py              # Settings
│   ├── logger.py              # Logging
│   ├── models.py              # Data models
│   ├── main.py                # CLI entry point
│   ├── video_processor/       # Video utilities
│   │   └── utils.py
│   ├── transcription/         # Whisper integration
│   │   └── whisper_local.py
│   └── graph/                 # LangGraph workflow
│       └── workflow.py
├── uploads/                   # Input videos
├── outputs/                   # Analysis results
├── logs/                      # Log files
├── requirements.txt
├── .env.example
└── README.md
```

---

## Cost Comparison

| Approach | Cost | Speed | Accuracy |
|----------|------|-------|----------|
| **Local (This)** | Free | Medium | 97% |
| OpenAI API | $0.006/min | Fast | 99% |
| Google Cloud | $0.006/min | Medium | 98% |
| Anthropic | $0.01-0.03 | Medium | 99% |

**This setup is completely free!** ✅

---

## Troubleshooting

### "ollama not found"

```bash
# Download from https://ollama.ai
# Or use Anthropic API instead:
USE_LOCAL_OLLAMA=false
ANTHROPIC_API_KEY=your_key
```

### "CUDA out of memory"

```bash
# Use smaller Whisper model
WHISPER_MODEL=tiny

# Or CPU only:
CUDA_VISIBLE_DEVICES="" python src/main.py analyze video.mp4
```

### "FFmpeg not found"

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
# Or download: https://ffmpeg.org/download.html
```

### Slow transcription

This is normal! Processing times:
- `tiny` model: 1-2 min for 10min video
- `base` model: 2-5 min for 10min video  
- `large` model: 10-15 min for 10min video

Start with `tiny` and upgrade if needed.

---

## Advanced Usage

### Custom Prompts

Edit prompts in `src/graph/workflow.py`:

```python
def summarize_node(state: GraphState) -> GraphState:
    prompt = f"""YOUR CUSTOM PROMPT HERE"""
    # ...
```

### Batch Processing

```python
from pathlib import Path
from src.main import analyze_video

videos_dir = Path("videos")
for video in videos_dir.glob("*.mp4"):
    result = analyze_video(str(video))
    print(f"{video.name}: {result['status']}")
```

### Docker Deployment

```bash
docker build -t video-analyzer .
docker run -v $(pwd)/videos:/app/uploads video-analyzer analyze video.mp4
```

---

## Performance Tips

1. **Start with Whisper `tiny`** - Fast, good enough for most cases
2. **Use Ollama locally** - No API rate limits
3. **Skip frames for speed** - Use `--skip-frames` flag
4. **Batch videos** - Process multiple files in parallel
5. **Use GPU** - Both Whisper and Ollama support GPU acceleration

---

## API Alternatives

### If you want to use APIs instead:

```bash
# OpenAI Whisper API (fast, $0.006/min)
pip install openai
# Update transcriber to use API

# Groq API (free tier available!)
pip install groq
# Update LLM to use Groq

# Claude API (high quality)
pip install anthropic
ANTHROPIC_API_KEY=sk-ant-...
USE_LOCAL_OLLAMA=false
```

---

## Contributing

Pull requests welcome! Please:
1. Fork the repo
2. Create feature branch
3. Test locally
4. Submit PR

---

## License

MIT - See LICENSE file

---

## Support

- 📖 **Docs**: Check README and code comments
- 🐛 **Issues**: Open on GitHub
- 💬 **Discussions**: Use GitHub Discussions
- 📧 **Email**: your@email.com

---

## Roadmap

- [ ] Web UI (Flask/FastAPI)
- [ ] Multi-language support
- [ ] Speaker diarization
- [ ] Keyword extraction
- [ ] Sentiment analysis
- [ ] PDF export
- [ ] Real-time streaming
- [ ] Batch API

---

## Acknowledgments

Built with:
- [LangGraph](https://langgraph.io) - Workflow orchestration
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- [Ollama](https://ollama.ai) - Local LLMs
- [LangChain](https://langchain.com) - LLM framework
- [FFmpeg](https://ffmpeg.org) - Video processing
- [OpenCV](https://opencv.org) - Computer vision

---

**Made with ❤️ using LangGraph**
