#!/usr/bin/env python3
"""
Timeline Video Generator - Entry Point
This script serves as the entry point for the Timeline Video Generator application.
It parses command-line arguments and passes them to the main module.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import the main module
try:
    from modules.main import generate_timeline_video
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a timeline video about a historical topic.')
    parser.add_argument('topic', type=str, help='The topic for the timeline video')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    return parser.parse_args()

def main():
    """Main function to execute the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Validate input
    if not args.topic or args.topic.strip() == "":
        logger.error("Topic cannot be empty")
        sys.exit(1)
    
    # Generate execution ID
    execution_id = datetime.now().strftime("%d%m%y%H%M")
    
    logger.info(f"Starting timeline video generation for topic: {args.topic}")
    logger.info(f"Execution ID: {execution_id}")
    
    try:
        # Call the main function from the main module
        result = generate_timeline_video(args.topic, execution_id)
        
        # Print the result
        logger.info(f"Video generation completed: {result}")
        print(f"Timeline video generated successfully: {result}")
        
    except Exception as e:
        logger.error(f"An error occurred during video generation: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()