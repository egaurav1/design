# src/models.py
"""Data models for video analysis"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    """Status of video processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoMetadata(BaseModel):
    """Metadata about the video"""
    filename: str
    file_path: str
    file_size_mb: float
    duration_seconds: float
    fps: float
    resolution: tuple[int, int]
    codec: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.now)

class TranscriptionResult(BaseModel):
    """Result of transcription"""
    text: str
    language: str = "en"
    confidence: Optional[float] = None
    duration_seconds: float = 0.0

class FrameAnalysis(BaseModel):
    """Analysis of a single frame"""
    frame_number: int
    timestamp_seconds: float
    image_path: str
    description: str
    size_bytes: int

class SummaryResult(BaseModel):
    """Generated summary"""
    short_summary: str = Field(..., description="2-3 sentences")
    medium_summary: str = Field(..., description="1 paragraph")
    long_summary: Optional[str] = None
    key_points: List[str] = []
    topics: List[str] = []

class AnalysisRequest(BaseModel):
    """Request to analyze a video"""
    video_path: str
    extract_frames: bool = True
    analyze_visual: bool = True
    transcribe: bool = True
    summarize: bool = True
    summary_type: str = "medium"  # short, medium, long

class AnalysisResult(BaseModel):
    """Complete analysis result"""
    video_metadata: VideoMetadata
    transcription: Optional[TranscriptionResult] = None
    frames: List[FrameAnalysis] = []
    visual_analysis: Optional[str] = None
    summary: Optional[SummaryResult] = None
    processing_time_seconds: float = 0.0
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class GraphState(BaseModel):
    """State object for LangGraph workflow"""
    video_path: str
    video_metadata: Optional[VideoMetadata] = None
    audio_path: Optional[str] = None
    transcription: Optional[TranscriptionResult] = None
    frames: List[FrameAnalysis] = []
    visual_analysis: Optional[str] = None
    summary: Optional[SummaryResult] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    error: Optional[str] = None
    processing_steps_completed: List[str] = []
    start_time: datetime = Field(default_factory=datetime.now)
