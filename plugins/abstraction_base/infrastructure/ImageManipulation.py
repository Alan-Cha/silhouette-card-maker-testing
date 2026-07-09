from io import BytesIO
from PIL import Image

async def prepare_for_image_manipulation(card_art: bytes) -> Image.Image:
    img = Image.open(BytesIO(card_art))
    return img
