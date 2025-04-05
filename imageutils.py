import base64
import requests
import constants
import pytesseract
from PIL import Image

class ImageUtils:
    @classmethod
    def extract_text_from_image(cls, image_path: str):
        # Open the image file
        image = Image.open(image_path)
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        return text

    @classmethod
    def generate_description_using_openai(cls, image_filepath: str) -> str:
        raise NotImplementedError()
