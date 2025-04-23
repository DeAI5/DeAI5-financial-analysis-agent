import os
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_image_with_openai(prompt: str) -> str | None:
    """
    Generates an image using the OpenAI DALL-E API based on the provided prompt.

    Args:
        prompt: The text prompt to guide image generation.

    Returns:
        The URL of the generated image, or None if an error occurs.
    """
    try:
        # Ensure the OpenAI API key is set in the environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            return None

        # Initialize the OpenAI client
        client = OpenAI(api_key=api_key)

        # Generate the image using DALL-E 3 (adjust model if needed)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024", # Standard size for DALL-E 3
            quality="standard", # Can be "hd" for higher quality/cost
            n=1, # Generate a single image
        )

        # Extract the image URL from the response
        image_url = response.data[0].url
        logger.info(f"Successfully generated image for prompt: '{prompt[:50]}...'")
        return image_url

    except Exception as e:
        logger.error(f"Error generating image with OpenAI: {e}")
        return None 