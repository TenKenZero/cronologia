"""
Timeline Video Generator - Main Module
This module orchestrates the entire process of generating timeline videos.
It coordinates calls to other modules for specific tasks.
"""

import os
import json
import logging
from typing import Dict, List, Any, Tuple

# Import other modules
from .gemini import (
    generate_timeline_stages,
    generate_voiceover_script,
    generate_image_prompts,
    generate_images
)
from .tts import generate_audio
from .graphics import create_video_clip, create_intro_clip, combine_video_clips

# Configure logging
logger = logging.getLogger(__name__)

def setup_directories(execution_id: str) -> Dict[str, str]:
    """
    Create necessary directories for the execution.
    
    Args:
        execution_id: Unique identifier for the execution
        
    Returns:
        Dictionary with paths to different directories
    """
    # Define base directories
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_dir = os.path.join(base_dir, "media", "image", execution_id)
    audio_dir = os.path.join(base_dir, "media", "audio", execution_id)
    video_dir = os.path.join(base_dir, "media", "video", execution_id)
    
    # Create directories if they don't exist
    for directory in [image_dir, audio_dir, video_dir]:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Created directory: {directory}")
    
    return {
        "base": base_dir,
        "image": image_dir,
        "audio": audio_dir,
        "video": video_dir
    }

def generate_timeline_video(topic: str, execution_id: str) -> str:
    """
    Generate a timeline video for a given topic.
    
    Args:
        topic: The topic for the timeline
        execution_id: Unique identifier for the execution
        
    Returns:
        Path to the generated video file
    """
    logger.info(f"Generating timeline video for topic: {topic}")
    
    # Setup directories
    dirs = setup_directories(execution_id)
    
    try:
        # Step 1: Generate timeline stages using Gemini API
        logger.info("Generating timeline stages...")
        timeline_data = generate_timeline_stages(topic)
        
        # Extract title and stages from the response
        title = timeline_data.get("title", f"Timeline of {topic}")
        stages = timeline_data.get("stages", [])
        
        logger.info(f"Generated timeline with title: {title} and {len(stages)} stages")
        
        # Step 2: Process each stage
        stage_clips = []
        
        for stage in stages:
            stage_order = stage.get("order")
            stage_name = stage.get("name")
            stage_desc = stage.get("description")
            
            logger.info(f"Processing stage {stage_order}: {stage_name}")
            
            # Generate voiceover script
            voiceover_script = generate_voiceover_script(topic, stage, stages)            
            
            # Generate audio for voiceover
            audio_path = generate_audio(
                voiceover_script, 
                os.path.join(dirs["audio"], f"{execution_id}_stage{stage_order}.mp3")
            )
            
            # Generate image prompts
            image_prompts = generate_image_prompts(topic, stage, stages, voiceover_script)
            # Generate images based on prompts
            image_paths = generate_images(
                image_prompts, 
                dirs["image"], 
                f"{execution_id}_stage{stage_order}"
            )

            if not image_paths or len(image_paths) < 3:
                logger.warning(f"Insufficient images generated. Creating placeholders.")
                image_paths = []
                for i in range(3):
                    image_path = os.path.join(dirs["image"], f"{execution_id}_stage{stage_order}_{i+1}.jpg")
                    from .graphics import create_placeholder_image
                    create_placeholder_image(image_path)
                    image_paths.append(image_path)
            
            # Create video clip for this stage
            clip_path = create_video_clip(
                image_paths,
                audio_path,
                stage_name,
                os.path.join(dirs["video"], f"{execution_id}_stage{stage_order}.mp4")
            )
            
            stage_clips.append(clip_path)
            logger.info(f"Created video clip for stage {stage_order}: {clip_path}")
        
        # Step 3: Create intro clip
        cover_path = os.path.join(dirs["base"], "media", "image", "cover.jpg")
        intro_clip_path = create_intro_clip(
            title,
            cover_path,
            os.path.join(dirs["video"], f"{execution_id}_intro.mp4")
        )
        
        # Step 4: Combine all clips into the final video
        all_clips = [intro_clip_path] + stage_clips
        final_video_path = os.path.join(dirs["video"], f"{execution_id}_final.mp4")
        
        result_path = combine_video_clips(all_clips, final_video_path)
        logger.info(f"Final video created at: {result_path}")
        
        return result_path
        
    except Exception as e:
        logger.error(f"Error in generate_timeline_video: {e}", exc_info=True)
        raise