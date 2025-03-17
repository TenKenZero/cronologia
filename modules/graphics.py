"""
Timeline Video Generator - Graphics Module
This module handles video creation, image processing, and combining
video clips for the timeline videos.
"""

import os
import logging
from typing import List, Optional

from moviepy import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip
)
from moviepy.audio.AudioClip import CompositeAudioClip, AudioClip, concatenate_audioclips
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)

def create_video_clip(
    image_paths: List[str],
    audio_path: str,
    caption: str,
    output_path: str
) -> str:
    """
    Create a video clip from images and audio.
    
    Args:
        image_paths: List of paths to the images to use
        audio_path: Path to the audio file
        caption: Caption text to display on the video
        output_path: Path where the video file will be saved
        
    Returns:
        Path to the generated video file
    """
    logger.info(f"Creating video clip with {len(image_paths)} images and audio from {audio_path}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Load audio file
        audio = AudioFileClip(audio_path)
        
        # Add 0.5 seconds of silence at the beginning and end
        audio_duration = audio.duration + 1.0  # 0.5s at beginning and end
        
        # Calculate duration for each image
        image_duration = audio_duration / 3
        
        # Create image clips
        image_clips = []
        for i, img_path in enumerate(image_paths):
            # Create a placeholder image if the file doesn't exist
            if not os.path.exists(img_path):
                logger.warning(f"Image file not found: {img_path}. Creating placeholder.")
                create_placeholder_image(img_path)
            
            # Load image and set duration
            img_clip = ImageClip(img_path, duration=image_duration)
            
            # Set start time
            # start_time = i * image_duration
            # img_clip = img_clip.set_start(start_time)
            
            image_clips.append(img_clip)
        
        # Create caption text clip
        txt_clip = TextClip(
            text=caption,
            font_size=50,
            color='white',
            bg_color=rgba_to_tuple('rgba(0,0,0,0.5)'),
            font='arial.ttf',
            size=(img_clip.w, None),
            method='label',
            text_align='center',
            horizontal_align='center',
            vertical_align='center',
            duration=audio_duration
        )
        
        # Combine image clips and text
        # clips = [txt_clip] + image_clips
        clipVideo = concatenate_videoclips(image_clips, method='chain')
        video = CompositeVideoClip([clipVideo, txt_clip])
        
        # Add audio with 0.5s offset
        silence = AudioClip(lambda t: 0, duration=0.5, fps=audio.fps) # Added fps=audio.fps
        audio = concatenate_audioclips([silence, audio, silence])
        video = video.with_audio(audio)
        
        # Write video file
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        logger.debug(f"Video clip created at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error in create_video_clip: {e}", exc_info=True)
        # Return the output path even if generation fails
        return output_path

def create_intro_clip(
    title: str,
    cover_image_path: str,
    output_path: str,
    duration: float = 2.0
) -> str:
    """
    Create an intro clip with the title and cover image.
    
    Args:
        title: Title text to display
        cover_image_path: Path to the cover image
        output_path: Path where the video file will be saved
        duration: Duration of the intro clip in seconds
        
    Returns:
        Path to the generated video file
    """
    logger.info(f"Creating intro clip with title: {title}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create a placeholder image if the cover image doesn't exist
        if not os.path.exists(cover_image_path):
            logger.warning(f"Cover image not found: {cover_image_path}. Creating placeholder.")
            create_placeholder_image(cover_image_path)
        
        # Load cover image
        img_clip = ImageClip(cover_image_path, duration=duration)
        
        # Create title text clip
        txt_clip = TextClip(
            text=title,
            font_size=50,
            color='white',
            bg_color=rgba_to_tuple('rgba(0,0,0,0.7)'),
            font='arial.ttf',
            size=(img_clip.w, None),
            method='label',
            text_align='center',
            horizontal_align='center',
            vertical_align='center',
            duration=duration
        )        
        
        # Combine image and text
        video = CompositeVideoClip([img_clip, txt_clip])
        
        # Write video file
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio=False,
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        logger.debug(f"Intro clip created at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error in create_intro_clip: {e}", exc_info=True)
        # Return the output path even if generation fails
        return output_path

def combine_video_clips(clip_paths: List[str], output_path: str) -> str:
    """
    Combine multiple video clips into a single video.
    
    Args:
        clip_paths: List of paths to the video clips
        output_path: Path where the combined video file will be saved
        
    Returns:
        Path to the generated video file
    """
    logger.info(f"Combining {len(clip_paths)} video clips")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Load video clips
        clips = []
        for path in clip_paths:
            if os.path.exists(path):
                from moviepy import VideoFileClip
                clip = VideoFileClip(path)
                clips.append(clip)
            else:
                logger.warning(f"Video clip not found: {path}")
        
        if not clips:
            raise ValueError("No valid video clips found")
        
        # Concatenate clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Write combined video file
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        logger.debug(f"Combined video created at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error in combine_video_clips: {e}", exc_info=True)
        # Return the output path even if generation fails
        return output_path

def create_placeholder_image(output_path: str, width: int = 1280, height: int = 720) -> None:
    """
    Create a placeholder image.
    
    Args:
        output_path: Path where the image will be saved
        width: Width of the image in pixels
        height: Height of the image in pixels
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create a simple placeholder image
        img = Image.new('RGB', (width, height), color=(100, 149, 237))  # Cornflower blue
        
        # Save the image
        img.save(output_path)
        logger.debug(f"Placeholder image created at {output_path}")
        
    except Exception as e:
        logger.error(f"Error in create_placeholder_image: {e}", exc_info=True)

def rgba_to_tuple(rgba_str: str) -> tuple:
    """Converts an RGBA string to an RGBA tuple."""
    rgba_str = rgba_str.replace('rgba(', '').replace(')', '')
    r, g, b, a = map(float, rgba_str.split(','))
    return (int(r), int(g), int(b), int(a * 255))