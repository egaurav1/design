# src/transcription/whisper_local.py
"""Local Whisper transcription (offline, no API key needed)"""

import whisper
from pathlib import Path
from typing import Optional
from ..logger import setup_logger
from ..config import settings
from ..models import TranscriptionResult
import time

logger = setup_logger(__name__)

class LocalWhisperTranscriber:
    """Transcribe audio using local Whisper model"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_size: tiny, base, small, medium, large
                       (larger = more accurate but slower)
        """
        self.model_size = model_size
        self.model = None
        logger.info(f"📥 Loading Whisper model: {model_size}")
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            self.model = whisper.load_model(self.model_size)
            logger.info(f"✅ Whisper model '{self.model_size}' loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio_path: str, language: str = "en") -> TranscriptionResult:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            TranscriptionResult with text, language, and other metadata
        """
        
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"🗣️  Transcribing {audio_path.name}...")
        
        start_time = time.time()
        
        try:
            # Transcribe with Whisper
            options = {
                "language": language,
                "verbose": False,  # Set True for detailed output
            }
            
            result = self.model.transcribe(str(audio_path), **options)
            
            transcription_time = time.time() - start_time
            
            # Get duration
            import librosa
            try:
                duration, _ = librosa.load(str(audio_path), sr=None)
                duration = len(duration) / 16000  # Approximate
            except:
                duration = 0.0
            
            transcription = TranscriptionResult(
                text=result["text"].strip(),
                language=result.get("language", language),
                duration_seconds=duration
            )
            
            word_count = len(transcription.text.split())
            logger.info(f"✅ Transcription complete!")
            logger.info(f"   Words: {word_count}")
            logger.info(f"   Language: {transcription.language}")
            logger.info(f"   Time: {transcription_time:.1f}s")
            
            return transcription
        
        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")
            raise

def create_transcriber(use_local: bool = True, 
                      model_size: str = "base") -> LocalWhisperTranscriber:
    """Factory function to create transcriber"""
    
    logger.info("🎙️  Initializing transcriber...")
    
    if use_local:
        logger.info("   Using local Whisper model (offline)")
        return LocalWhisperTranscriber(model_size=model_size)
    else:
        logger.error("   Non-local transcriber not implemented yet")
        raise NotImplementedError("Use local Whisper or set API key for remote")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        
        # Create transcriber
        transcriber = LocalWhisperTranscriber(model_size="base")
        
        # Transcribe
        result = transcriber.transcribe(audio_file)
        
        print("\n" + "="*60)
        print("TRANSCRIPTION RESULT")
        print("="*60)
        print(f"Language: {result.language}")
        print(f"Duration: {result.duration_seconds:.1f}s")
        print(f"Words: {len(result.text.split())}")
        print("\nText:")
        print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
