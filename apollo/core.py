import google.generativeai as genai
import requests
from pathlib import Path
from typing import Optional
from apollo.models import Content

class GeminiAPIHandler:
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, content: Content) -> str:
        """
        Generates a text response from the Gemini API based on the provided Content.
        """
        system_prompt = ""
        if content.image_data:
            # OSINT Mode prompt
            system_prompt = (
                "You are an OSINT expert. Analyze the provided image to answer the question. "
                "Provide a very concise and direct answer. Give a specific location, object, "
                "or person if possible. Do not write long explanations."
            )
            image_part = {'mime_type': content.mime_type, 'data': content.image_data}
            api_contents = [image_part, f"{system_prompt}\n\nQuestion: {content.prompt}"]
        else:
            # Quick Search Mode prompt
            system_prompt = (
                "You are a CTF expert. Provide a concise, short answer to the user's question. "
                "Keep the response under 100 words. If recommending tools, list them briefly. "
                "Do not write long paragraphs or give word vomit."
            )
            api_contents = f"{system_prompt}\n\nQuestion: {content.prompt}"

        response = self.model.generate_content(api_contents)
        return response.text

class FileHandler:
    def get_image_from_path(self, path: str) -> tuple[bytes, str]:
        """Reads a local image file and returns its bytes and MIME type."""
        image_path = Path(path)
        if not image_path.is_file():
            raise FileNotFoundError(f"File not found at '{image_path}'")
        
        mime_type = f"image/{image_path.suffix.lstrip('.').lower()}"
        supported_types = ["image/jpeg", "image/png", "image/webp"]
        if mime_type not in supported_types:
            raise ValueError(f"Unsupported file type '{mime_type}'. Supported: {', '.join(supported_types)}.")

        with open(image_path, "rb") as f:
            return f.read(), mime_type

    def get_image_from_url(self, url: str) -> tuple[bytes, str]:
        """Downloads an image from a URL and returns its bytes and MIME type."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            mime_type = response.headers.get('Content-Type', 'image/jpeg')
            return response.content, mime_type
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error fetching image from URL: {e}")