# src/video_processor/utils.py
"""Utilities for video processing"""

import subprocess
import os
from pathlib import Path
from typing import Tuple
import cv2
from ..logger import setup_logger
from ..config import settings
from ..models import VideoMetadata
from datetime import datetime

logger = setup_logger(__name__)

def get_video_metadata(video_path: str) -> VideoMetadata:
    """Extract metadata from video file"""
    
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Use ffprobe to get metadata
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,codec_name,duration",
            "-of", "csv=p=0",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip().split(',')
        
        width = int(output[0])
        height = int(output[1])
        fps_str = output[2]
        codec = output[3]
        duration = float(output[4]) if len(output) > 4 else 0.0
        
        # Parse FPS (can be in format like "30/1" or "29.97")
        if '/' in fps_str:
            num, den = map(float, fps_str.split('/'))
            fps = num / den
        else:
            fps = float(fps_str)
        
    except Exception as e:
        logger.warning(f"Could not get full metadata with ffprobe: {e}")
        # Fallback to OpenCV
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        codec = None
        cap.release()
    
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    
    metadata = VideoMetadata(
        filename=video_path.name,
        file_path=str(video_path),
        file_size_mb=file_size_mb,
        duration_seconds=duration,
        fps=fps,
        resolution=(width, height),
        codec=codec,
        uploaded_at=datetime.now()
    )
    
    logger.info(f"✅ Video metadata extracted: {metadata.filename}")
    logger.info(f"   Duration: {duration:.2f}s, Resolution: {width}x{height}, FPS: {fps:.2f}")
    
    return metadata

def extract_audio(video_path: str, output_dir: Path = None) -> str:
    """Extract audio from video using ffmpeg"""
    
    if output_dir is None:
        output_dir = settings.TEMP_DIR
    
    video_path = Path(video_path)
    output_path = output_dir / f"{video_path.stem}_audio.mp3"
    
    logger.info(f"🎙️ Extracting audio from {video_path.name}...")
    
    try:
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-q:a", "9", "-n", str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Audio extracted: {output_path.name} ({size_mb:.2f} MB)")
            return str(output_path)
        else:
            raise Exception("Audio file not created")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg error: {e.stderr.decode()}")
        raise
    except Exception as e:
        logger.error(f"❌ Error extracting audio: {e}")
        raise

def extract_frames(video_path: str, output_dir: Path = None, 
                  frames_per_minute: int = 2) -> list[str]:
    """Extract key frames from video"""
    
    if output_dir is None:
        output_dir = settings.TEMP_DIR / "frames"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    video_path = Path(video_path)
    logger.info(f"🎬 Extracting frames from {video_path.name}...")
    
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    logger.info(f"   Duration: {duration:.2f}s, FPS: {fps:.2f}, Total frames: {total_frames}")
    
    # Calculate frame interval
    interval = int(fps * 60 / frames_per_minute) if fps > 0 else 1
    frame_count = 0
    frame_paths = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                # Resize to reduce file size
                frame = cv2.resize(frame, (640, 480))
                
                frame_number = len(frame_paths)
                frame_path = output_dir / f"frame_{frame_number:03d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(str(frame_path))
                
                logger.debug(f"   ✓ Frame {frame_number + 1} extracted")
            
            frame_count += 1
        
        cap.release()
        logger.info(f"✅ Extracted {len(frame_paths)} frames")
        return frame_paths
    
    except Exception as e:
        logger.error(f"❌ Error extracting frames: {e}")
        cap.release()
        raise

def cleanup_temp_files(paths: list[str]):
    """Clean up temporary files"""
    
    for path in paths:
        try:
            Path(path).unlink()
            logger.debug(f"🗑️  Deleted {Path(path).name}")
        except Exception as e:
            logger.warning(f"Could not delete {path}: {e}")

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
        metadata = get_video_metadata(video_file)
        print(f"Metadata: {metadata}")
        
        audio_file = extract_audio(video_file)
        print(f"Audio: {audio_file}")
        
        frames = extract_frames(video_file)
        print(f"Frames: {len(frames)} extracted")
