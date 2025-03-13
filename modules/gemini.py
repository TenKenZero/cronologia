"""
Timeline Video Generator - Gemini API Module
This module handles interactions with Google's Gemini API for generating
timeline stages, voiceover scripts, and image prompts.
"""

import os
import json
import logging
from typing import Dict, List, Any

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    logging.error(f"Failed to configure Gemini API: {e}")
    raise

# Configure logging
logger = logging.getLogger(__name__)

def generate_timeline_stages(topic: str) -> Dict[str, Any]:
    """
    Generate timeline stages for a given topic.
    
    Args:
        topic: The topic for the timeline
        
    Returns:
        Dictionary containing title and stages for the timeline
    """
    logger.info(f"Generating timeline stages for topic: {topic}")
    
    try:
        # Construct prompt for Gemini
        prompt = f"""
        Create a historical timeline for the topic: "{topic}".
        
        Generate a JSON object with the following structure:
        {{
            "title": "A short, catchy title for the timeline video (e.g., 'Evolution of {topic}')",
            "stages": [
                {{
                    "order": 1,
                    "name": "Short name for the first stage (max 5 words)",
                    "description": "Detailed description of this historical stage (50-100 words)"
                }},
                ...more stages...
            ]
        }}
        
        Guidelines:
        - Include 4-6 significant stages in the historical evolution
        - Each stage name should be concise (3-5 words)
        - Each description should focus on key developments, changes, or milestones
        - Ensure chronological order
        - Include specific dates or time periods when relevant
        - Focus on historically accurate information
        
        Respond with ONLY the JSON object and nothing else.
        """
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Parse the response
        content = response.text
        
        # Extract JSON from the response
        # This handles cases where the model might add markdown code blocks
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        # Parse JSON
        timeline_data = json.loads(json_str)
        
        # Validate the structure
        if "title" not in timeline_data or "stages" not in timeline_data:
            raise ValueError("Invalid response structure from Gemini API")
        
        logger.debug(f"Generated timeline with {len(timeline_data['stages'])} stages")
        return timeline_data
        
    except Exception as e:
        logger.error(f"Error in generate_timeline_stages: {e}", exc_info=True)
        # Return a minimal valid structure in case of error
        return {
            "title": f"Timeline of {topic}",
            "stages": [
                {
                    "order": 1,
                    "name": f"History of {topic}",
                    "description": f"An overview of the historical evolution of {topic}."
                }
            ]
        }

def generate_voiceover_script(topic: str, stage: Dict[str, Any], all_stages: List[Dict[str, Any]]) -> str:
    """
    Generate a voiceover script for a specific timeline stage.
    
    Args:
        topic: The main topic of the timeline
        stage: The current stage data
        all_stages: List of all stages in the timeline
        
    Returns:
        Voiceover script text
    """
    logger.info(f"Generating voiceover script for stage {stage.get('order')}: {stage.get('name')}")
    
    try:
        # Construct prompt for Gemini
        prompt = f"""
        Create a voice-over script for a historical timeline video about "{topic}".
        
        This script is for the stage: "{stage.get('name')}"
        
        Full description of this stage:
        "{stage.get('description')}"
        
        Guidelines:
        - The script should be 10-15 seconds when read aloud (approximately 30-45 words)
        - Use clear, engaging language suitable for a general audience
        - Focus on the most important historical facts and developments
        - Begin with a smooth transition if this isn't the first stage
        - End with a hook to the next stage if this isn't the last stage
        - Use a conversational tone that works well for voice narration
        - Include specific dates or time periods when relevant
        
        Respond with ONLY the voice-over script and nothing else.
        """
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Extract the script
        script = response.text.strip()
        
        logger.debug(f"Generated script with {len(script.split())} words")
        return script
        
    except Exception as e:
        logger.error(f"Error in generate_voiceover_script: {e}", exc_info=True)
        # Return a minimal script in case of error
        return f"During this period, {stage.get('name')} marked an important milestone in the history of {topic}. {stage.get('description')[:50]}..."

def generate_image_prompts(topic: str, stage: Dict[str, Any], all_stages: List[Dict[str, Any]], voiceover_script: str) -> List[str]:
    """
    Generate image prompts for a specific timeline stage.
    
    Args:
        topic: The main topic of the timeline
        stage: The current stage data
        all_stages: List of all stages in the timeline
        voiceover_script: The voiceover script for this stage
        
    Returns:
        List of image prompts
    """
    logger.info(f"Generating image prompts for stage {stage.get('order')}: {stage.get('name')}")
    
    try:
        # Construct prompt for Gemini
        prompt = f"""
        Create 3 detailed image generation prompts that visually represent the following historical stage:
        
        Topic: "{topic}"
        Stage: "{stage.get('name')}"
        Description: "{stage.get('description')}"
        Voice-over script: "{voiceover_script}"
        
        Guidelines for the image prompts:
        - Each prompt should describe a different visual aspect of this historical stage
        - Focus on historical accuracy and educational value
        - Include details about style, composition, lighting, and important visual elements
        - Prompts should be detailed enough for an AI image generator to create compelling visuals
        - Each prompt should be 2-3 sentences long
        - The images should form a coherent visual narrative for this stage
        
        Format your response as a JSON array of 3 strings, each representing one image prompt.
        Example: ["Prompt 1", "Prompt 2", "Prompt 3"]
        
        Respond with ONLY the JSON array and nothing else.
        """
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Parse the response
        content = response.text
        
        # Extract JSON from the response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        # Parse JSON
        image_prompts = json.loads(json_str)
        
        # Ensure we have exactly 3 prompts
        if len(image_prompts) != 3:
            logger.warning(f"Expected 3 image prompts, got {len(image_prompts)}. Adjusting...")
            if len(image_prompts) < 3:
                # Add generic prompts if we have fewer than 3
                while len(image_prompts) < 3:
                    image_prompts.append(f"Historical illustration of {topic} during the {stage.get('name')} period.")
            else:
                # Truncate if we have more than 3
                image_prompts = image_prompts[:3]
        
        logger.debug(f"Generated {len(image_prompts)} image prompts")
        return image_prompts
        
    except Exception as e:
        logger.error(f"Error in generate_image_prompts: {e}", exc_info=True)
        # Return generic prompts in case of error
        return [
            f"Historical illustration of {topic} during the {stage.get('name')} period.",
            f"Detailed visual representation of {stage.get('name')} in the evolution of {topic}.",
            f"Historical scene showing key aspects of {topic} during {stage.get('name')}."
        ]