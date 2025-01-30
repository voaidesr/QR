import numpy as np
from PIL import Image

def read_qr(image_path: str) -> np.array:
    """
    Decodes an image to a boolean NumPy array.

    Parameters:
    image_path (str): The path to the image file.
    """
    im = Image.open(image_path).convert('RGB')  # Ensure it's in RGB mode
    np_array = np.array(im)

    # Convert rgb values to True and False
    return np.all(np_array == [255, 255, 255], axis=-1)

# TODO: In the future, fina a way to make this function more robust
#       for example, the case where the code can be surrounded by black pixels
def crop_qr(image: np.array) -> np.array:
    """
    Crop the QR code from the given image and resize it to 25x25 pixels.
    This function finds the bounding box of the QR code in the input image by
    identifying rows and columns that contain black pixels. It then crops the
    image to this bounding box and resizes the cropped QR code to 25x25 pixels
    while preserving its structure.
    Args:
        image (np.array): A 2D numpy array representing the binary image of the QR code,
                          where 0 represents white pixels and 1 represents black pixels.
    Returns:
        np.array: A 2D numpy array of shape (25, 25) representing the resized QR code,
                  where True represents black pixels and False represents white pixels.
    """
    
    # Find the bounding box of the QR code (remove extra white space)
    rows = np.any(~image, axis=1)  # Find rows with black pixels
    cols = np.any(~image, axis=0)  # Find cols with black pixels
    rmin, rmax = np.where(rows)[0][[0, -1]]  # Get first and last row with black
    cmin, cmax = np.where(cols)[0][[0, -1]]  # Get first and last col with black

    # Crop to the detected QR code area
    cropped_qr = image[rmin:rmax+1, cmin:cmax+1]

    # Resize to 25x25 while preserving structure
    im = Image.fromarray(cropped_qr.astype(np.uint8) * 255)
    im_resized = im.resize((25, 25), Image.NEAREST)
    resized_qr = np.array(im_resized) > 128 

    return resized_qr