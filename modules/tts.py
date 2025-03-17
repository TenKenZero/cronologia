"""
Timeline Video Generator - Text-to-Speech Module
This module handles interactions with Google's Text-to-Speech API
to generate audio narration for the timeline videos.
"""

import os
import logging
from typing import Optional

from google.cloud import texttospeech
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize TTS client
try:
    client = texttospeech.TextToSpeechClient()
except Exception as e:
    logger.error(f"Failed to initialize Text-to-Speech client: {e}")
    client = None

def generate_audio(text: str, output_path: str, voice_name: str = "es-US-Chirp-HD-D") -> str:
    """
    Generate an audio file from the given text using Google's Text-to-Speech API.
    
    Args:
        text: The text to convert to speech
        output_path: Path where the audio file will be saved
        voice_name: The voice to use for speech synthesis
        
    Returns:
        Path to the generated audio file
    """
    logger.info(f"Generating audio for text of length {len(text)}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if TTS client is available
        if client is None:
            raise RuntimeError("Text-to-Speech client is not initialized")
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-US",
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        # Select the type of audio file to return
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # Normal speed
            pitch=0.0,  # Default pitch
            volume_gain_db=0.0  # Default volume
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Write the response to the output file
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
            logger.debug(f"Audio content written to {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error in generate_audio: {e}", exc_info=True)
        # Create a placeholder audio file path if generation fails
        logger.warning(f"Returning placeholder audio path: {output_path}")
        return output_path