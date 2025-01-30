import numpy as np
from PIL import Image

def decode_qr(image_path: str) -> np.array:
    """
    Decodes a BMP image to a NumPy array and prints it.

    Parameters:
    image_path (str): The path to the BMP image file.
    """
    im = Image.open(image_path).convert('RGB')  # Ensure it's in RGB mode
    return np.array(im) 
    