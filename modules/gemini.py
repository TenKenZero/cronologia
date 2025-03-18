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
        # Other stages for context
        all_stages_text = ""
        if all_stages:
            all_stages_text = "Estas son todas las etapas del video (para referencia): ".join([f"\n*   **Título de la etapa:** {s.get('name')} \n*   **Descripción completa de la etapa:** {s.get('description')} \n*   **Número de etapa:** {s.get('order')} \n" for s in all_stages])

        # Construct prompt for Gemini
        prompt = f"""
        Actúa como un guionista profesional de documentales y videos cortos para redes sociales. Tu tarea es escribir el guion para la voz en off de *una* etapa específica de un video cronológico sobre "{topic}".
        
        {all_stages_text}
        
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
        *   **Formato de salida:** Responde *SOLO* con el guion de la voz en off. No incluyas encabezados, pies de página, número de palabras, ni ningún otro texto que no deba ser leído en voz alta. Tampoco incluyas asteriscos (*). Tampoco dividas el guion en etapas, secciones o subtitulos; este es referido a una sola etapa. El texto debe ser directamente utilizable por un generador de texto a voz, utiliza los signos de puntuación adecuados.
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
    
def generate_voiceover_intro_script(topic: str, all_stages: List[Dict[str, Any]]) -> str:
    """
    Generate a voiceover script for the introduction of the timeline video.

    Args:
        topic: The main topic of the timeline
        all_stages: List of all stages in the timeline

    Returns:
        Voiceover intro script text
    """
    logger.info(f"Generating voiceover intro script for topic: {topic}")

    try:
        # All stages for context
        all_stages_text = ""
        if all_stages:
            all_stages_text = "Estas son todas las etapas del video: ".join([f"\n*   **Título de la etapa:** {s.get('name')} \n*   **Descripción completa de la etapa:** {s.get('description')} \n*   **Número de etapa:** {s.get('order')} \n" for s in all_stages])
        
        # Construct prompt for Gemini
        prompt = f"""
        Actúa como un guionista profesional de documentales y videos cortos para redes sociales. Tu tarea es escribir el guion para la voz en off de la *introducción* de un video cronológico sobre "{topic}".

        {all_stages_text}

        Instrucciones para el guion de la voz en off de la introducción:

        * Duración: El guion debe tener una duración aproximada de 3-5 segundos al ser leído en voz alta. La brevedad y el impacto inicial son clave.
        * Lenguaje: Usa un lenguaje claro, conciso, atractivo y que genere curiosidad en el espectador. El objetivo es enganchar a la audiencia desde el principio. Evita la jerga técnica innecesaria.
        * Contenido: Utiliza las siguientes formulas para generar un guion corto y efectivo:
            * Comienza con una pregunta para retar los conocimientos del espectador. Por ejemplo, "¿Qué sabes realmente sobre...?".
            * Comienza con una pregunta que aliente la curiosidad del espectador. Por ejemplo, "¿Alguna vez te has preguntado...?".
            * Comienza con una afirmación sorprendente o un dato poco conocido. Por ejemplo, "Lo que no sabías sobre...".
            * Comienza con una anécdota breve y relevante que se encuentre entre la informacion de las etapas del video. Por ejemplo, "Hace siglos, en un lugar remoto...".
            * Comienza preguntando un hecho curioso o poco conocido que se encuentre entre la informacion de las etapas del video.. Por ejemplo, "¿Sabías que...?".
            * Finaliza la introducción con una transición suave hacia la primera etapa de la cronología. Por ejemplo, "Descubre cómo todo comenzó en este video".
            * Finaliza con una frase que invite a la audiencia a seguir viendo. Por ejemplo, "No te pierdas la increíble historia de...".
            * Finaliza con una una invitación a la acción. Por ejemplo, "Acompáñanos en este viaje a través de la historia de ...".
            * Finaliza con una afirmación que genere expectativa. Por ejemplo, "Lo que estás a punto de ver cambiará tu perspectiva sobre...".
            * Finaliza con una invitacion segura. Por ejemplo, "Descubre esto y mas en el video de hoy".
        
        * Tono: Adopta un tono entusiasta, informativo y amigable, que invite al espectador a seguir viendo el video.
        * Formato de salida: Responde *SOLO* con el guion de la voz en off. No incluyas encabezados, subtitulos, pies de página, número de palabras, ni ningún otro texto que no deba ser leído en voz alta. Tampoco incluyas asteriscos (*). El texto debe ser directamente utilizable por un generador de texto a voz, utiliza los signos de puntuación adecuados.
        """

        # Call Gemini API
        response = client.models.generate_content(model=textModel, contents=prompt)

        # Extract the script
        script = response.text.strip()

        logger.debug(f"Generated intro script with {len(script.split())} words")
        return script

    except Exception as e:
        logger.error(f"Error in generate_voiceover_intro_script: {e}", exc_info=True)
        # Return a minimal script in case of error
        return f"Bienvenidos. Hoy exploraremos la historia de {topic} a través de su cronología."

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
        # All stages for context
        all_stages_text = ""
        if all_stages:
            all_stages_text = "Estas son todas las etapas del video: ".join([f"\n*   **Título de la etapa:** {s.get('name')} \n*   **Descripción completa de la etapa:** {s.get('description')} \n*   **Número de etapa:** {s.get('order')} \n" for s in all_stages])
        
        # Construct prompt for Gemini
        prompt = f"""
        Actúa como un director de arte experto en la creación de imágenes históricas y documentales, con un profundo conocimiento de la IA generadora de imágenes. Tu tarea es elaborar *tres* prompts detallados para una IA generadora de imágenes. Estos prompts deben describir visualmente una determinada etapa histórica del tema: "{topic}".

        {all_stages_text}

        Aquí tienes la información de la etapa particular para la que debes crear los prompts:
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
    
def generate_cover_image_prompts(topic: str, all_stages: List[Dict[str, Any]]) -> List[str]:
    """
    Generate image prompts for the cover of the video.
    
    Args:
        topic: The main topic of the timeline
        all_stages: List of all stages in the timeline
        
    Returns:
        List of image prompts for cover images
    """
    logger.info(f"Generating cover image prompts for topic: {topic}")
    
    try:
        # All stages for context
        all_stages_text = ""
        if all_stages:
            all_stages_text = "Estas son todas las etapas del video: ".join([f"\n*   **Título de la etapa:** {s.get('name')} \n*   **Descripción completa de la etapa:** {s.get('description')} \n*   **Número de etapa:** {s.get('order')} \n" for s in all_stages])
        
        # Construct prompt for Gemini
        prompt = f"""
        Actúa como un director de arte experto en la creación de imágenes impactantes y representativas para portadas de videos históricos, con un profundo conocimiento de la IA generadora de imágenes. Tu tarea es elaborar *tres* prompts detallados para una IA generadora de imágenes. Estos prompts deben describir visualmente la evolución histórica completa del tema: "{topic}", de una manera atractiva e informativa para la portada de un video corto (TikTok, Instagram Reels).

        {all_stages_text}

        Instrucciones para los prompts de las imágenes de portada:

        * **Diversidad Visual:** Cada prompt debe proponer un *enfoque visual diferente* para la portada del video. Evita la redundancia. Piensa en diferentes conceptos, estilos y composiciones.
        * **Representación General:** Las imágenes deben representar visualmente la *totalidad* de la evolución histórica del tema, no solo una etapa específica. Intenta evocar una sensación del viaje histórico completo.
        * **Atractivo Visual:** Las imágenes deben ser visualmente atractivas y llamativas para captar la atención del espectador en una plataforma de redes sociales. Considera el uso de elementos visuales impactantes y una composición interesante.
        * **Informativo:** Aunque atractivas, las imágenes también deben ser informativas y dar una idea clara del tema del video.
        * **Posibles Enfoques:** Considera las siguientes ideas (puedes combinarlas o proponer otras):
            * **Metáfora Visual:** Utiliza una metáfora visual que represente la evolución del tema (por ejemplo, una semilla que crece hasta convertirse en un árbol para representar el crecimiento de una idea).
            * **Montaje o Collage:** Un montaje sutil de elementos visuales clave de diferentes etapas de la cronología.
            * **Representación Simbólica:** Utiliza símbolos o iconos que representen el tema y su transformación a lo largo del tiempo.
            * **Imagen Conceptual:** Una imagen que transmita el concepto general de la evolución histórica del tema de manera abstracta pero reconocible.
        * **Detalles Específicos:** Incluye detalles específicos sobre:
            * **Estilo:** ¿Debería ser una imagen moderna y minimalista, una ilustración con un toque histórico, una representación artística abstracta, etc.?
            * **Composición:** ¿Cuál debería ser el punto focal? ¿Debería haber algún elemento en primer plano y otros en segundo plano? ¿Debería haber algún tipo de marco o borde?
            * **Iluminación:** ¿Cómo es la iluminación general? ¿Brillante y llamativa, tenue y misteriosa, etc.?
            * **Colores:** ¿Qué paleta de colores debería predominar? ¿Colores vibrantes para atraer la atención, colores más sobrios para un tono histórico, etc.?
            * **Elementos Visuales Clave:** Describe cualquier objeto, figura o elemento específico que *debería* aparecer o que *podría* aparecer para representar el tema y su evolución.
        * **Longitud:** Cada prompt debe tener entre 2 y 4 oraciones. Sé descriptivo y conciso.
        * **Narrativa Visual Coherente:** Los tres prompts, aunque diferentes entre sí, deben mantener un enfoque coherente sobre el tema del video.
        * **Imagen Sensible:** Las imágenes a crear deben seguir las normas de seguridad de Google y no contener contenido sensible.
        * **Idioma de Salida:** Los prompts deben estar escritos en idioma inglés.
        * **Formato de Salida:** Responde *SOLO* con un array JSON de tres strings. Cada string representa un prompt de imagen. Ejemplo:
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
                    image_prompts.append(f"Historical illustration of the evolution of {topic} through time, showing key transformations in a visually striking composition.")
            else:
                # Truncate if we have more than 3
                image_prompts = image_prompts[:3]
        
        logger.debug(f"Generated {len(image_prompts)} cover image prompts")
        return image_prompts
        
    except Exception as e:
        logger.error(f"Error in generate_cover_image_prompts: {e}", exc_info=True)
        # Return generic prompts in case of error
        return [
            f"Historical illustration of the evolution of {topic} through time, showing key transformations in a visually striking composition.",
            f"A compelling visual metaphor representing the journey of {topic} through history, with symbolic elements transitioning from past to present.",
            f"Dynamic collage showing the most significant milestones in the history of {topic}, arranged in a visually appealing timeline format."
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
                    except Exception as e:
                        logger.error(f"Other error processing image data: {e}")
                else:
                    logger.warning(f"No image generated for prompt {i+1}. Creating placeholder.")
                    
            except Exception as e:
                logger.error(f"Error generating image {i + 1}: {e}", exc_info=True)
        
        return image_paths
        
    except Exception as e:
        logger.error(f"Error in generate_images: {e}", exc_info=True)
        return []
    
def generate_cover_images(prompts: List[str], output_dir: str, prefix: str) -> List[str]:
    """
    Generate cover images based on text prompts using Google's Gemini API (Imagen).

    Args:
        prompts: List of text prompts for cover image generation.
        output_dir: Directory where the images will be saved.
        prefix: Prefix for the image filenames.

    Returns:
        List of paths to the generated cover images.
    """
    logger.info(f"Generating cover images from {len(prompts)} prompts with prefix {prefix}")

    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        cover_image_paths = []
        
        # Generate cover images for each prompt
        for i, prompt in enumerate(prompts):
            try:
                logger.debug(f"Generating cover image for prompt: {prompt}")
                
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
                    cover_image_path = os.path.join(output_dir, f"{prefix}_cover{i + 1}.jpg")
                    try:
                        image = Image.open(BytesIO(generated_image.image.image_bytes))
                        image.save(cover_image_path)
                        cover_image_paths.append(cover_image_path)
                        logger.debug(f"Cover image saved to {cover_image_path}")
                    except UnidentifiedImageError as e:
                        logger.error(f"Error opening cover image data: {e}. Likely invalid image format.")
                    except Exception as e:
                        logger.error(f"Other error processing cover image data: {e}")
                else:
                    logger.warning(f"No cover image generated for prompt {i+1}. Creating placeholder.")
                    
            except Exception as e:
                logger.error(f"Error generating cover image {i + 1}: {e}", exc_info=True)
        
        return cover_image_paths
        
    except Exception as e:
        logger.error(f"Error in generate_cover_images: {e}", exc_info=True)
        return []
