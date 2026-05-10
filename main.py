# src/main.py
"""Main entry point for video analyzer"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from ..logger import setup_logger
from ..config import settings
from ..models import GraphState
from ..graph.workflow import create_workflow
import json

logger = setup_logger(__name__)

def analyze_video(video_path: str, 
                 extract_frames: bool = True,
                 analyze_visual: bool = True,
                 transcribe: bool = True,
                 summarize: bool = True) -> dict:
    """
    Analyze a video file
    
    Args:
        video_path: Path to video file
        extract_frames: Whether to extract frames
        analyze_visual: Whether to analyze frames
        transcribe: Whether to transcribe audio
        summarize: Whether to generate summary
    
    Returns:
        Analysis results
    """
    
    logger.info("🚀 Starting video analysis...")
    logger.info(f"   Video: {video_path}")
    
    # Validate file exists
    video_file = Path(video_path)
    if not video_file.exists():
        logger.error(f"❌ File not found: {video_path}")
        return {"error": f"File not found: {video_path}"}
    
    try:
        # Create initial state
        state = GraphState(
            video_path=str(video_file.resolve()),
            start_time=datetime.now()
        )
        
        # Create and run workflow
        logger.info("📊 Creating workflow graph...")
        app = create_workflow()
        
        logger.info("🔄 Running workflow...")
        final_state = app.invoke(state)
        
        # Prepare result
        result = {
            "status": final_state.status.value,
            "video_metadata": final_state.video_metadata.dict() if final_state.video_metadata else None,
            "transcription": final_state.transcription.dict() if final_state.transcription else None,
            "summary": final_state.summary.dict() if final_state.summary else None,
            "frames_extracted": len(final_state.frames),
            "processing_steps": final_state.processing_steps_completed,
            "error": final_state.error
        }
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def main():
    """CLI interface"""
    
    parser = argparse.ArgumentParser(
        description="🎬 Video Analyzer - AI-powered video analysis with LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py analyze video.mp4
  python src/main.py analyze video.mp4 --skip-visual
  python src/main.py config
  python src/main.py test
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a video")
    analyze_parser.add_argument("video", help="Path to video file")
    analyze_parser.add_argument("--skip-transcription", action="store_true",
                              help="Skip audio transcription")
    analyze_parser.add_argument("--skip-frames", action="store_true",
                              help="Skip frame extraction")
    analyze_parser.add_argument("--skip-visual", action="store_true",
                              help="Skip visual analysis")
    analyze_parser.add_argument("--skip-summary", action="store_true",
                              help="Skip summarization")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--transcribe", action="store_true",
                            help="Test transcription only")
    test_parser.add_argument("--llm", action="store_true",
                            help="Test LLM only")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "analyze":
        result = analyze_video(
            args.video,
            extract_frames=not args.skip_frames,
            analyze_visual=not args.skip_visual,
            transcribe=not args.skip_transcription,
            summarize=not args.skip_summary
        )
        
        # Print result
        print("\n" + "="*60)
        print("ANALYSIS RESULT")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))
        print("="*60)
        
        if result.get("error"):
            return 1
        return 0
    
    elif args.command == "config":
        print("\n" + "="*60)
        print("CONFIGURATION")
        print("="*60)
        print(f"Project Root: {settings.PROJECT_ROOT}")
        print(f"Video Upload Dir: {settings.VIDEO_UPLOAD_DIR}")
        print(f"Output Dir: {settings.OUTPUT_DIR}")
        print(f"Temp Dir: {settings.TEMP_DIR}")
        print(f"Logs Dir: {settings.LOGS_DIR}")
        print()
        print(f"LLM Settings:")
        print(f"  Use Local Ollama: {settings.USE_LOCAL_OLLAMA}")
        print(f"  Ollama Model: {settings.OLLAMA_MODEL}")
        print(f"  Whisper Model: {settings.WHISPER_MODEL}")
        print()
        print(f"Feature Flags:")
        print(f"  Frame Extraction: {settings.ENABLE_FRAME_EXTRACTION}")
        print(f"  Visual Analysis: {settings.ENABLE_VISUAL_ANALYSIS}")
        print(f"  Transcription: {settings.ENABLE_TRANSCRIPTION}")
        print(f"  Summarization: {settings.ENABLE_SUMMARIZATION}")
        print("="*60 + "\n")
        return 0
    
    elif args.command == "test":
        print("\n" + "="*60)
        print("TESTING COMPONENTS")
        print("="*60)
        
        test_results = {}
        
        # Test Whisper
        if args.transcribe or not args.llm:
            print("\n🎙️  Testing Whisper...")
            try:
                from .transcription.whisper_local import LocalWhisperTranscriber
                transcriber = LocalWhisperTranscriber(model_size="tiny")
                test_results["whisper"] = "✅ OK"
                print("   ✅ Whisper model loaded")
            except Exception as e:
                test_results["whisper"] = f"❌ {e}"
                print(f"   ❌ Error: {e}")
        
        # Test LLM
        if args.llm or not args.transcribe:
            print("\n🤖  Testing LLM...")
            try:
                from .llm.llm_interface import create_llm_client
                llm = create_llm_client(use_local=settings.USE_LOCAL_OLLAMA)
                test_results["llm"] = "✅ OK"
                print("   ✅ LLM client initialized")
            except Exception as e:
                test_results["llm"] = f"❌ {e}"
                print(f"   ❌ Error: {e}")
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        for component, result in test_results.items():
            print(f"{component}: {result}")
        print("="*60 + "\n")
        return 0
    
    elif args.command == "version":
        print("\nVideo Analyzer v1.0.0")
        print("Built with LangGraph and open-source tools")
        print("https://github.com/yourusername/video-analyzer\n")
        return 0
    
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
