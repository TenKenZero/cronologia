# Timeline Video Generator

## Overview

The Timeline Video Generator is a Python application designed to automate the creation of engaging historical divulgation videos for platforms like TikTok and Instagram Reels. Given a topic, the application generates videos in a "Timeline" format, showcasing the historical evolution of the subject. Each stage of the timeline includes:

* **AI-generated voice-over:** Based on a concise explanation of the historical stage.
* **AI-generated explanation:** A short description of each historical stage.
* **AI-generated images:** Visual depictions of the historical stage.
* **AI-generated background music:** Music appropriate to the topic.

## Table of Contents

* [Overview](#overview)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Folder Structure](#folder-structure)
* [Modules Description](#modules-description)
* [Contributing](#contributing)
* [License](#license)
* [Support](#support)

## Installation

1.  **Clone the repository** (if applicable).
2.  **Navigate to the project directory** in your terminal.
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This command will install the necessary Python libraries, including:
    * `google-genai>=1.5.0`: For interacting with the Gemini API.
    * `google-cloud-texttospeech>=2.14.1`: For Google Text-to-Speech functionality.
    * `moviepy>=1.0.3`: For video editing operations.
    * `python-dotenv>=1.0.0`: For managing environment variables.
    * `Pillow>=9.5.0`: For image processing.
    * `requests>=2.31.0`: For making HTTP requests.
    * `pydantic>=2.4.0`: For data validation.

## Configuration

1.  **Create a `.env` file** in the root directory of the project.
2.  **Add the following environment variables** to the `.env` file:

    ```dotenv
    # API Keys
    GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>

    # Language of the Input and the Videos
    LANGUAGE=es
    ```

    * Replace `<YOUR_GEMINI_API_KEY>` with your actual Gemini API key. You will need to obtain this from Google Cloud AI Platform.
    * Set the `LANGUAGE` variable to the desired language for the input and generated videos. Currently, "en" (English) and "es" (Spanish) are supported.

## Usage

To run the application, use the following command in your terminal:

```bash
python app.py "<Your Historical Topic>" [--debug]
```

  * Replace `"<Your Historical Topic>"` with the specific historical topic you want to generate a timeline video for. For example:

    ```bash
    python app.py "History of Automobiles"
    ```

  * The `--debug` flag is optional. If included, it will enable debug mode, providing more detailed logging output.

The application will then proceed to generate the timeline video, saving the output in the `media/video/<execution_id>` directory, where `<execution_id>` is a timestamp representing the execution time. The console will also display the path to the generated video upon successful completion. Application logs will be saved in the `app.log` file.

## Folder Structure
```
./
├── app.py             # Entry point of the application
├── requirements.txt   # List of Python dependencies
├── .env               # Environment variables (API keys, settings)
├── app.log            # Application log file (will be created during execution)
│
├── media/             # Directory for storing generated media
│   ├── image/         # Subdirectory for generated images
│   ├── audio/         # Subdirectory for generated audio files
│   └── video/         # Subdirectory for generated video files
│
└── modules/           # Directory containing Python modules
    ├── __init__.py    # Initializes the modules directory as a Python package
    ├── main.py        # Main orchestration module for video generation
    ├── gemini.py      # Module for interacting with the Gemini API
    ├── tts.py         # Module for Text-to-Speech functionality
    └── graphics.py    # Module for handling image and video processing
```

## Modules Description

* **`main.py`**: This module serves as the central orchestrator of the video generation process. It calls functions from other modules to generate timeline stages, voice-overs, images, and finally combines them into a video.
* **`gemini.py`**: This module handles all interactions with the Google Gemini API. It is responsible for generating the timeline stages, voice-over scripts, and image prompts based on the provided topic and language.
* **`tts.py`**: This module utilizes the Google Cloud Text-to-Speech API to convert the generated voice-over scripts into audio files in the specified language.
* **`graphics.py`**: This module uses the `moviepy` library to create video clips from the generated images and audio, adding captions, an intro clip, and finally combining all the clips into the final timeline video.

## Contributing

Contributions to the Timeline Video Generator are welcome. Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License

MIT License

## Support

For any questions or issues, please contact leningeniero@gmail.com.