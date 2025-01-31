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

def is_finder_pattern(block: np.array) -> bool:
    # Checks if a given 7x7 block in the QR matrix matches the finder pattern.
    if block.shape != (7, 7):
        return False

    # Expected finder pattern structure
    expected_pattern = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ])

    return np.array_equal(block, expected_pattern)

def detect_finder_patterns(qr_matrix: np.array):
    # Detects the positions of finder patterns in the QR code.
    pattern_positions = []  # Store (row, col) of detected finder pattern centers
    rows, cols = qr_matrix.shape

    for i in range(rows - 6):
        for j in range(cols - 6):
            block = qr_matrix[i:i+7, j:j+7]
            if is_finder_pattern(block):
                pattern_positions.append((i + 3, j + 3))  # Store the center of the pattern

    return pattern_positions

def is_qr_code(qr_matrix: np.array) -> bool:
    # Checks if the given matrix is likely a QR code by detecting finder patterns.
    # A valid QR code must have exactly three finder patterns
    return len(detect_finder_patterns(qr_matrix)) == 3