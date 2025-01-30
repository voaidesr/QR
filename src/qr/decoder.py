import numpy as np
from PIL import Image

# TODO: Find why this doesn't work for black/white BMP files?
def decode_qr(image_path: str):
    """
    Decodes a BMP image to a NumPy array and prints it.

    Parameters:
    image_path (str): The path to the BMP image file.
    """
    im = Image.open(image_path).convert('L')  # Convert to grayscale
    image_array = np.array(im)  # Convert to NumPy array
    
    # Print image matrix
    for row in image_array:
        print(" ".join(f"{val:3}" for val in row))  # Print values with spacing
