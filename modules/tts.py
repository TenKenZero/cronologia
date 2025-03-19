"""
Timeline Video Generator - Text-to-Speech Module
This module handles interactions with Google's Text-to-Speech API
to generate audio narration for the timeline videos with multilingual support.
"""

import os
import logging
from typing import Optional

from google.cloud import texttospeech
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get language setting from environment variables (default to English if not set)
LANGUAGE = os.getenv("LANGUAGE", "en").lower()
if LANGUAGE not in ["en", "es"]:
    logging.warning(f"Unsupported language: {LANGUAGE}. Defaulting to English.")
    LANGUAGE = "en"

# Voice configuration per language
VOICE_CONFIG = {
    "en": {
        "voice_name": "en-US-Chirp-HD-D",
        "language_code": "en-US"
    },
    "es": {
        "voice_name": "es-US-Chirp-HD-D",
        "language_code": "es-US"
    }
}

# Configure logging
logger = logging.getLogger(__name__)

# Initialize TTS client
try:
    client = texttospeech.TextToSpeechClient()
except Exception as e:
    logger.error(f"Failed to initialize Text-to-Speech client: {e}")
    client = None

def generate_audio(text: str, output_path: str, voice_name: Optional[str] = None) -> str:
    """
    Generate an audio file from the given text using Google's Text-to-Speech API.
    
    Args:
        text: The text to convert to speech
        output_path: Path where the audio file will be saved
        voice_name: The voice to use for speech synthesis (optional, will use language-specific default if not specified)
        
    Returns:
        Path to the generated audio file
    """
    logger.info(f"Generating audio for text of length {len(text)} in {LANGUAGE}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if TTS client is available
        if client is None:
            raise RuntimeError("Text-to-Speech client is not initialized")
        
        # Use the provided voice_name or get the default for the current language
        if voice_name is None:
            voice_name = VOICE_CONFIG[LANGUAGE]["voice_name"]
        
        # Get the language code for the current language
        language_code = VOICE_CONFIG[LANGUAGE]["language_code"]
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
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