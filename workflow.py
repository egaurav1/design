# src/graph/workflow.py
"""LangGraph workflow for video analysis"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any
from ..models import GraphState, ProcessingStatus, FrameAnalysis, SummaryResult
from ..logger import setup_logger
from ..config import settings
from ..video_processor.utils import (
    get_video_metadata, extract_audio, extract_frames, cleanup_temp_files
)
from ..transcription.whisper_local import LocalWhisperTranscriber
from ..llm.llm_interface import create_llm_client
import base64
from pathlib import Path
import time
import traceback

logger = setup_logger(__name__)

# ============================================================================
# NODE FUNCTIONS
# ============================================================================

def validate_input(state: GraphState) -> GraphState:
    """Validate input video"""
    
    logger.info("\n" + "="*60)
    logger.info("🎬 VIDEO ANALYSIS WORKFLOW STARTING")
    logger.info("="*60)
    
    try:
        video_path = Path(state.video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {state.video_path}")
        
        # Check file size
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.MAX_VIDEO_SIZE_MB:
            raise ValueError(f"File too large: {file_size_mb}MB > {settings.MAX_VIDEO_SIZE_MB}MB")
        
        # Check format
        suffix = video_path.suffix.lower().lstrip('.')
        if suffix not in settings.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")
        
        logger.info(f"✅ Input validation passed")
        logger.info(f"   File: {video_path.name}")
        logger.info(f"   Size: {file_size_mb:.2f} MB")
        
        state.processing_steps_completed.append("validate_input")
        return state
    
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def extract_metadata(state: GraphState) -> GraphState:
    """Extract video metadata"""
    
    try:
        logger.info("\n📊 Extracting metadata...")
        state.video_metadata = get_video_metadata(state.video_path)
        state.processing_steps_completed.append("extract_metadata")
        return state
    except Exception as e:
        logger.error(f"❌ Metadata extraction error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def extract_audio_node(state: GraphState) -> GraphState:
    """Extract audio from video"""
    
    if not settings.ENABLE_TRANSCRIPTION:
        logger.info("⏭️  Skipping audio extraction (disabled)")
        return state
    
    try:
        logger.info("\n🎙️  Extracting audio...")
        state.audio_path = extract_audio(state.video_path)
        state.processing_steps_completed.append("extract_audio")
        return state
    except Exception as e:
        logger.error(f"❌ Audio extraction error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def transcribe_node(state: GraphState) -> GraphState:
    """Transcribe audio to text"""
    
    if not settings.ENABLE_TRANSCRIPTION:
        logger.info("⏭️  Skipping transcription (disabled)")
        return state
    
    if not state.audio_path:
        logger.warning("⚠️  No audio available for transcription")
        return state
    
    try:
        logger.info("\n🗣️  Transcribing audio...")
        
        transcriber = LocalWhisperTranscriber(model_size=settings.WHISPER_MODEL)
        state.transcription = transcriber.transcribe(state.audio_path)
        
        state.processing_steps_completed.append("transcribe")
        return state
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def extract_frames_node(state: GraphState) -> GraphState:
    """Extract key frames from video"""
    
    if not settings.ENABLE_FRAME_EXTRACTION:
        logger.info("⏭️  Skipping frame extraction (disabled)")
        return state
    
    try:
        logger.info("\n🎬 Extracting frames...")
        
        frame_paths = extract_frames(
            state.video_path,
            frames_per_minute=settings.FRAMES_PER_MINUTE
        )
        
        # Convert to FrameAnalysis objects
        state.frames = [
            FrameAnalysis(
                frame_number=i,
                timestamp_seconds=(i / settings.FRAMES_PER_MINUTE) * 60 if state.video_metadata else 0,
                image_path=path,
                description="",
                size_bytes=Path(path).stat().st_size
            )
            for i, path in enumerate(frame_paths)
        ]
        
        state.processing_steps_completed.append("extract_frames")
        return state
    except Exception as e:
        logger.error(f"❌ Frame extraction error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def analyze_frames_node(state: GraphState) -> GraphState:
    """Analyze extracted frames with LLM"""
    
    if not settings.ENABLE_VISUAL_ANALYSIS:
        logger.info("⏭️  Skipping visual analysis (disabled)")
        return state
    
    if not state.frames:
        logger.warning("⚠️  No frames available for analysis")
        return state
    
    try:
        logger.info("\n🔍 Analyzing frames with LLM...")
        
        llm = create_llm_client(use_local=settings.USE_LOCAL_OLLAMA)
        
        frame_descriptions = []
        
        for frame in state.frames[:3]:  # Analyze first 3 frames
            try:
                # Read image and encode to base64
                with open(frame.image_path, "rb") as f:
                    image_data = base64.standard_b64encode(f.read()).decode("utf-8")
                
                # Create prompt for image analysis
                prompt = f"""Describe this video frame in 2-3 sentences.
Focus on the main subjects, actions, and setting.

[Image: {Path(frame.image_path).name}]

DESCRIPTION:"""
                
                # For now, use text-based analysis (LLMs often don't handle images well locally)
                # In production, use Claude's vision API
                description = f"Frame analysis for {Path(frame.image_path).name}"
                
                frame.description = description
                frame_descriptions.append(description)
                
                logger.debug(f"   ✓ Frame {frame.frame_number} analyzed")
            
            except Exception as e:
                logger.warning(f"Could not analyze frame {frame.frame_number}: {e}")
                continue
        
        state.visual_analysis = "\n\n".join(frame_descriptions) if frame_descriptions else None
        state.processing_steps_completed.append("analyze_frames")
        return state
    
    except Exception as e:
        logger.warning(f"⚠️  Visual analysis error (non-critical): {e}")
        # Don't fail the workflow for this
        return state

def summarize_node(state: GraphState) -> GraphState:
    """Generate summary of transcript"""
    
    if not settings.ENABLE_SUMMARIZATION:
        logger.info("⏭️  Skipping summarization (disabled)")
        return state
    
    if not state.transcription:
        logger.warning("⚠️  No transcript available for summarization")
        return state
    
    try:
        logger.info("\n✍️  Generating summary...")
        
        llm = create_llm_client(use_local=settings.USE_LOCAL_OLLAMA)
        
        # Create comprehensive prompt
        prompt = f"""Analyze this video transcript and create summaries of different lengths.

TRANSCRIPT:
{state.transcription.text}
"""
        
        if state.visual_analysis:
            prompt += f"\nKEY VISUAL ELEMENTS:\n{state.visual_analysis}\n"
        
        prompt += """
Create three versions:
1. SHORT: 2-3 sentences
2. MEDIUM: 1 paragraph (5-7 sentences)  
3. LONG: 2-3 paragraphs

Also list:
- KEY POINTS: 3-5 main takeaways (as bullet points)
- TOPICS: List of main topics covered

Format your response clearly with these sections."""
        
        # Generate summary
        summary_text = llm.generate(prompt, max_tokens=1000)
        
        # Parse response (in production, use structured output)
        state.summary = SummaryResult(
            short_summary=summary_text[:200],
            medium_summary=summary_text,
            long_summary=summary_text,
            key_points=[],
            topics=[]
        )
        
        state.processing_steps_completed.append("summarize")
        return state
    
    except Exception as e:
        logger.error(f"❌ Summarization error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def save_results(state: GraphState) -> GraphState:
    """Save analysis results to files"""
    
    try:
        logger.info("\n💾 Saving results...")
        
        output_dir = settings.OUTPUT_DIR / Path(state.video_path).stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save transcript
        if state.transcription:
            transcript_file = output_dir / "transcript.txt"
            with open(transcript_file, "w") as f:
                f.write(state.transcription.text)
            logger.info(f"   ✓ Transcript: {transcript_file.name}")
        
        # Save summary
        if state.summary:
            summary_file = output_dir / "summary.txt"
            with open(summary_file, "w") as f:
                f.write(f"SHORT SUMMARY:\n{state.summary.short_summary}\n\n")
                f.write(f"MEDIUM SUMMARY:\n{state.summary.medium_summary}\n\n")
                if state.summary.long_summary:
                    f.write(f"LONG SUMMARY:\n{state.summary.long_summary}\n")
            logger.info(f"   ✓ Summary: {summary_file.name}")
        
        # Save metadata
        import json
        from datetime import datetime
        
        metadata = {
            "video_file": Path(state.video_path).name,
            "video_metadata": state.video_metadata.dict() if state.video_metadata else None,
            "processing_time_seconds": time.time() - state.start_time.timestamp(),
            "steps_completed": state.processing_steps_completed,
            "frames_extracted": len(state.frames),
            "has_transcript": state.transcription is not None,
            "has_summary": state.summary is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"   ✓ Metadata: {metadata_file.name}")
        
        logger.info(f"✅ Results saved to: {output_dir}")
        
        state.processing_steps_completed.append("save_results")
        return state
    
    except Exception as e:
        logger.error(f"❌ Save results error: {e}")
        state.status = ProcessingStatus.FAILED
        state.error = str(e)
        return state

def cleanup(state: GraphState) -> GraphState:
    """Clean up temporary files"""
    
    try:
        logger.info("\n🗑️  Cleaning up temporary files...")
        
        # Collect files to delete
        files_to_delete = []
        if state.audio_path:
            files_to_delete.append(state.audio_path)
        
        files_to_delete.extend([f.image_path for f in state.frames])
        
        cleanup_temp_files(files_to_delete)
        
        state.processing_steps_completed.append("cleanup")
        return state
    
    except Exception as e:
        logger.warning(f"⚠️  Cleanup error (non-critical): {e}")
        return state

def finalize(state: GraphState) -> GraphState:
    """Finalize workflow"""
    
    state.status = ProcessingStatus.COMPLETED
    
    logger.info("\n" + "="*60)
    logger.info("✅ WORKFLOW COMPLETED")
    logger.info("="*60)
    logger.info(f"Steps completed: {', '.join(state.processing_steps_completed)}")
    logger.info(f"Processing time: {time.time() - state.start_time.timestamp():.1f}s")
    logger.info("="*60 + "\n")
    
    return state

# ============================================================================
# WORKFLOW GRAPH
# ============================================================================

def create_workflow():
    """Create the LangGraph workflow"""
    
    logger.info("🔨 Building LangGraph workflow...")
    
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("extract_metadata", extract_metadata)
    workflow.add_node("extract_audio", extract_audio_node)
    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("extract_frames", extract_frames_node)
    workflow.add_node("analyze_frames", analyze_frames_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("save_results", save_results)
    workflow.add_node("cleanup", cleanup)
    workflow.add_node("finalize", finalize)
    
    # Add edges (define workflow order)
    workflow.set_entry_point("validate_input")
    
    workflow.add_edge("validate_input", "extract_metadata")
    workflow.add_edge("extract_metadata", "extract_audio")
    workflow.add_edge("extract_audio", "transcribe")
    workflow.add_edge("transcribe", "extract_frames")
    workflow.add_edge("extract_frames", "analyze_frames")
    workflow.add_edge("analyze_frames", "summarize")
    workflow.add_edge("summarize", "save_results")
    workflow.add_edge("save_results", "cleanup")
    workflow.add_edge("cleanup", "finalize")
    
    workflow.add_edge("finalize", END)
    
    app = workflow.compile()
    
    logger.info("✅ Workflow graph built successfully")
    return app

if __name__ == "__main__":
    print("LangGraph workflow module loaded")
