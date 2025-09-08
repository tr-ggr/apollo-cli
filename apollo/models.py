from typing import Optional

class Content:
    def __init__(self, prompt: str, image_data: Optional[bytes] = None, mime_type: Optional[str] = None):
        self.prompt = prompt
        self.image_data = image_data
        self.mime_type = mime_type