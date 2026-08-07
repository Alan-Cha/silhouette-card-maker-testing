#==============================================================================
# offset.py 
#     Duplex printing alignment. Feeds offset_pdf.py.
#==============================================================================

import os
import json 
import math

from pydantic import BaseModel, ValidationError
from .paths import Paths

from PIL import Image, ImageChops 

DATA_PATH = Paths.root / "data"
OFFSET_DATA_PATH = DATA_PATH / "offset_data.json"

class OffsetData(BaseModel):
    x_offset: int = 0 
    y_offset: int = 0
    angle_offset: float = 0.0

def save_offset(x_offset: int, y_offset: int, angle_offset: float = 0.0) -> None:
    os.makedirs(DATA_PATH, exist_ok=True)
    
    with open(OFFSET_DATA_PATH, 'w') as offset_file:
        offset_data = OffsetData(x_offset=x_offset, y_offset=y_offset,angle_offset=angle_offset)
        _ = offset_file.write(offset_data.model_dump_json(indent=4))
    print("Offset data saved!")

def load_saved_offset() -> OffsetData | None:
    if not OFFSET_DATA_PATH.is_file():
        return None 
    
    with open(OFFSET_DATA_PATH, 'r') as offset_file:
        try:
            data = json.load(offset_file)
            return OffsetData(**data)
        except json.JSONDecodeError as e:
            print(f"Cannot decode offset JSON: {e}")
        except ValidationError as e:
            print(f"Cannot validate offset data: {e}")

    return None

def offset_images(
    images: list[Image.Image],
    x_offset: int,
    y_offset: int,
    ppi: int,
    angle_offset: float = 0.0,
) -> list[Image.Image]:
    result_images: list[Image.Image] = []
     
    # Only add offset to back images and account for orientation flip 
    add_offset = False
    x_back_offset = math.floor(-x_offset * ppi / 300)
    y_back_offset = math.floor(y_offset * ppi / 300)

    for image in images:
        if add_offset:
            result = ImageChops.offset(image, x_back_offset, y_back_offset)
            if angle_offset != 0.0:
                result = result.rotate(
                    -angle_offset, 
                    center = (image.width / 2, image.height / 2), 
                    fillcolor="white"
                )
            result_images.append(result)
        else:
            result_images.append(image)
        add_offset = not add_offset
    return result_images



        
