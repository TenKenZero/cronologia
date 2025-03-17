"""
Timeline Video Generator - Gemini API Module
This module handles interactions with Google's Gemini API for generating
timeline stages, voiceover scripts, and image prompts.
"""

import os
import json
import logging
from typing import Dict, List, Any
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    #genai.configure(api_key=GEMINI_API_KEY)
    textModel = "gemini-2.0-pro-exp-02-05"
    imageModel = "imagen-3.0-generate-002"
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
        Actúa como un experto en historia y en creación de contenido para redes sociales. Tu tarea es crear una cronología histórica concisa y atractiva para un video corto (estilo TikTok o Instagram Reels) sobre el tema: "{topic}".

        Genera un objeto JSON con la siguiente estructura.  Respeta estrictamente el formato, sin añadir texto adicional antes o después del JSON:

        {{
        "title": "Un título corto y llamativo para el video.  Debe captar la atención y ser adecuado para redes sociales. (Ejemplo: 'La Evolución de {topic}')",
        "stages": [
            {{
            "order": 1,
            "name": "Nombre corto para la primera etapa (máximo 5 palabras, idealmente 3).  Este texto aparecerá como pie de página en el video, así que debe ser muy conciso.",
            "description": "Descripción detallada de esta etapa histórica (entre 50 y 80 palabras).  Concéntrate en los desarrollos, cambios o hitos clave. Incluye fechas o períodos específicos *si son relevantes y fáciles de entender para una audiencia general*. Prioriza la claridad y el impacto sobre la exhaustividad."
            }},
            {{
            "order": 2,
            "name": "Nombre corto para la segunda etapa (máximo 5 palabras, idealmente 3).",
            "description": "Descripción detallada de la segunda etapa (entre 50 y 80 palabras).  Mantén un tono coherente con la etapa anterior."
            }},
            {{
            "order": 3,
            "name": "Nombre corto para la tercera etapa (máximo 5 palabras, idealmente 3).",
            "description": "Descripción detallada de la tercera etapa (entre 50 y 80 palabras)."
            }},
            {{
            "order": 4,
            "name": "Nombre corto para la cuarta etapa (máximo 5 palabras, idealmente 3).",
            "description": "Descripción detallada de la cuarta etapa (entre 50 y 80 palabras)."
            }}

        ]
        }}

        Instrucciones y consideraciones adicionales:

        *   **Número de etapas:** Incluye *exactamente* 4 etapas.  Cuatro etapas es un buen número para mantener el video corto y dinámico.  Si el tema requiere más, considera dividirlo en múltiples videos (por ejemplo, "Parte 1", "Parte 2").
        *   **Orden cronológico:** Asegúrate de que las etapas estén en estricto orden cronológico.
        *   **Precisión histórica:** La información debe ser históricamente precisa.  Aunque se busca un formato atractivo, la veracidad es fundamental.
        *   **Tono:** El tono debe ser divulgativo pero entretenido.  Imagina que estás explicando la historia a alguien que no sabe nada del tema, pero quieres mantener su interés. Evita la jerga académica excesiva.
        *   **Formato de salida:**  Responde *SOLO* con el objeto JSON. No incluyas ninguna otra palabra, frase, saludo, despedida, o explicación.  El JSON debe ser válido y directamente utilizable por tu aplicación Python.
        * **Énfasis en el formato del JSON:**  El formato que proporcionaste es correcto.  La estructura anidada de `stages` con `order`, `name` y `description` es clara.  Asegúrate de que Gemini *siempre* devuelva un JSON válido.
        """
        
        # Call Gemini API
        response = client.models.generate_content(model=textModel, contents=prompt)
        
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
        Actúa como un guionista profesional de documentales y videos cortos para redes sociales. Tu tarea es escribir el guion para la voz en off de *una* etapa específica de un video cronológico sobre "{topic}".

        Esta es la información de la etapa para la que debes escribir el guion:

        *   **Título de la etapa:** "{stage.get('name')}"
        *   **Descripción completa de la etapa:** "{stage.get('description')}"
        *   **Número de etapa:** "{stage.get('order')}"

        Instrucciones para el guion de la voz en off:

        *   **Duración:** El guion debe tener una duración aproximada de 10-15 segundos al ser leído en voz alta. Esto equivale a unas 30-45 palabras.  *Sé muy preciso con el conteo de palabras*.  La brevedad es clave.
        *   **Lenguaje:** Usa un lenguaje claro, conciso y atractivo, adecuado para una audiencia general (no académica). Evita la jerga técnica innecesaria.
        *   **Enfoque:** Concéntrate en los *hechos y desarrollos históricos más importantes y visualmente interesantes* de esta etapa.  Selecciona la información que mejor se traduzca a imágenes.
        *   **Transiciones:**
            *   Si esta *no* es la primera etapa (es decir, si `stage.get('order')` es mayor que 1), comienza el guion con una *breve* transición desde la etapa anterior.  Algo como "Luego...", "Más tarde...", "Posteriormente...", "A continuación...", o una frase corta que conecte lógicamente con el contenido anterior.
            *   Si esta *no* es la última etapa, termina con un *gancho* o una pregunta que invite a ver la siguiente etapa.  Por ejemplo: "¿Pero qué pasó después?", "Esto llevaría a...", "El siguiente paso sería crucial...", "Sin embargo, todo estaba a punto de cambiar...".
        *   **Tono:** Adopta un tono conversacional y ameno, como si estuvieras contando una historia interesante a un amigo. Evita la formalidad excesiva.
        *   **Fechas:** Incluye fechas o períodos *solo si son absolutamente esenciales* para comprender el evento y *si son fáciles de recordar*.  En videos cortos, demasiadas fechas pueden ser confusas.
        * **Formato de salida:** Responde *SOLO* con el guion de la voz en off. No incluyas encabezados, pies de página, ni ningún otro texto que no deba ser leído en voz alta. El texto debe ser directamente utilizable por un generador de texto a voz.
        """
        
        # Call Gemini API
        response = client.models.generate_content(model=textModel, contents=prompt)
        
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
        Actúa como un director de arte experto en la creación de imágenes históricas y documentales, con un profundo conocimiento de la IA generadora de imágenes. Tu tarea es elaborar *tres* prompts detallados para una IA generadora de imágenes. Estos prompts deben describir visualmente la siguiente etapa histórica:

        *   **Tema general:** "{topic}"
        *   **Título de la etapa:** "{stage.get('name')}"
        *   **Descripción de la etapa:** "{stage.get('description')}"
        *   **Guion de la voz en off:** "{voiceover_script}"
        *   **Número de etapa:** "{stage.get('order')}"

        Instrucciones para los prompts de imágenes:

        *   **Diversidad Visual:** Cada prompt debe describir un *aspecto visual diferente* de esta etapa histórica.  Evita la redundancia.  Piensa en diferentes ángulos, planos (general, medio, primer plano), y composiciones.
        *   **Precisión Histórica:** La precisión histórica es *fundamental*.  Los prompts deben reflejar fielmente la época, la vestimenta, la arquitectura, la tecnología y cualquier otro detalle relevante.
        *   **Valor Educativo:** Prioriza los elementos visuales que tengan un valor educativo y que ayuden a comprender mejor la etapa histórica.
        *   **Detalles:** Incluye detalles específicos sobre:
            *   **Estilo:** ¿Debería ser una imagen fotorrealista, una ilustración, una pintura (y de qué estilo)? ¿Debe emular la estética de una fotografía antigua?
            *   **Composición:** ¿Cómo deben estar dispuestos los elementos en la imagen? ¿Cuál es el punto focal?
            *   **Iluminación:** ¿Cómo es la iluminación? ¿Natural, artificial, dramática, tenue?
            *   **Colores:** ¿Qué paleta de colores predomina? ¿Son colores vibrantes, apagados, monocromáticos?
            *   **Elementos Visuales Clave:** Describe con precisión los objetos, personas, edificios, etc., que deben aparecer en la imagen.
            * **Relación con el guion:** Considera cómo se complementa cada imagen con el guion de voz en off. No es necesario que la imagen describa *literalmente* cada palabra del guion, pero sí que exista una conexión temática y visual.

        *   **Longitud:** Cada prompt debe tener entre 2 y 4 oraciones. Sé descriptivo pero conciso.
        *   **Narrativa Visual Coherente:** Las tres imágenes, en conjunto, deben formar una narrativa visual coherente para esta etapa. Deben poder entenderse como una secuencia.
        *   **Imagenes sensibles:** Las imagenes a crear deben seguir las normas de seguirdad de google y no contener contenido sensible.
        *   **Idioma de salida:** Los prompts deben estar escritos en idioma inglés.
        *   **Formato de Salida:** Responde *SOLO* con un array JSON de tres strings. Cada string representa un prompt de imagen.  Ejemplo:
            ```json
            ["Prompt 1", "Prompt 2", "Prompt 3"]
            ```
            No incluyas ningún texto adicional antes o después del array JSON.
        """
        
        # Call Gemini API
        response = client.models.generate_content(model=textModel, contents=prompt)
        
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
    
def generate_images(prompts: List[str], output_dir: str, prefix: str) -> List[str]:
    """
    Generate images based on text prompts using Google's Gemini API (Imagen).

    Args:
        prompts: List of text prompts for image generation.
        output_dir: Directory where the images will be saved.
        prefix: Prefix for the image filenames.

    Returns:
        List of paths to the generated images.
    """
    logger.info(f"Generating images from {len(prompts)} prompts with prefix {prefix}")

    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        image_paths = []
        
        # Generate images for each prompt
        for i, prompt in enumerate(prompts):
            try:
                logger.debug(f"Generating image for prompt: {prompt}")
                
                # Generate image using the Imagen model
                response = client.models.generate_images(
                    model=imageModel,  # 'imagen-3.0-generate-002' as defined at the top of the file
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="9:16"  # Assuming landscape format for timeline videos
                    )
                )
                
                # Process the generated image
                if response.generated_images:
                    # Get the first generated image
                    generated_image = response.generated_images[0]
                    
                    # Save the image
                    image_path = os.path.join(output_dir, f"{prefix}_{i + 1}.jpg")
                    try:
                        image = Image.open(BytesIO(generated_image.image.image_bytes))
                        image.save(image_path)
                        image_paths.append(image_path)
                        logger.debug(f"Image saved to {image_path}")
                    except UnidentifiedImageError as e:
                        logger.error(f"Error opening image data: {e}. Likely invalid image format.")
                        _create_placeholder_image(output_dir, prefix, i)
                        image_paths.append(os.path.join(output_dir, f"{prefix}_{i + 1}.jpg"))
                    except Exception as e:
                        logger.error(f"Other error processing image data: {e}")
                        _create_placeholder_image(output_dir, prefix, i)
                        image_paths.append(os.path.join(output_dir, f"{prefix}_{i + 1}.jpg"))
                else:
                    logger.warning(f"No image generated for prompt {i+1}. Creating placeholder.")
                    _create_placeholder_image(output_dir, prefix, i)
                    image_paths.append(os.path.join(output_dir, f"{prefix}_{i + 1}.jpg"))
                    
            except Exception as e:
                logger.error(f"Error generating image {i + 1}: {e}", exc_info=True)
                _create_placeholder_image(output_dir, prefix, i)
                image_paths.append(os.path.join(output_dir, f"{prefix}_{i + 1}.jpg"))
        
        return image_paths
        
    except Exception as e:
        logger.error(f"Error in generate_images: {e}", exc_info=True)
        return []


def _create_placeholder_image(output_dir: str, prefix: str, index: int):
    """Creates a simple placeholder image (helper function)."""
    image_path = os.path.join(output_dir, f"{prefix}_{index + 1}.jpg")
    img = Image.new('RGB', (256, 256), color='gray')  # Create a gray image
    img.save(image_path)