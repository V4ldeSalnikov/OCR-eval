from base64 import b64encode
from io import BytesIO

from PIL import Image


def image_to_png_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    return b64encode(buffer.getvalue()).decode("ascii")
