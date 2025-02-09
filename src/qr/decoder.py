import numpy as np
from PIL import Image
import cv2
from reedsolo import RSCodec, ReedSolomonError
import qr.constants as constants

# https://stackoverflow.com/questions/60359398/python-detect-a-qr-code-from-an-image-and-crop-using-opencv
def find_qr_in_image(image_path: str, draw_rectangle: bool = False) -> tuple:
    """
    Detects and extracts the QR code from an image.
    Args:
        image_path (str): The file path to the input image.
    Returns:
        np.array: The extracted QR code region of interest (ROI) as an image array.
    This function performs the following steps:
    1. Loads the image from the specified path.
    2. Converts the image to grayscale.
    3. Applies Gaussian blur to reduce noise.
    4. Uses Otsu's thresholding to convert the image to a binary image.
    5. Applies morphological closing to close small gaps in the binary image.
    6. Finds contours in the binary image.
    7. Filters contours to identify potential QR code regions based on contour properties.
    """
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    # This helps remove high-frequency noise and retains the low-frequency components.
    blur = cv2.GaussianBlur(gray, (9,9), 0)

    # Apply Otsu's threshold
    # https://en.wikipedia.org/wiki/Otsu%27s_method
    # Converts the blurred grayscale image into a binary (black and white) image.
    # cv2.THRESH_BINARY_INV inverts the colors (QR codes are typically black on white).
    # cv2.THRESH_OTSU automatically determines the best threshold value to separate the QR code from the background.
    # Author's note: This is magic to me, but it's 2AM and I don't have the energy to get into frequency domain filtering.
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph close
    # https://en.wikipedia.org/wiki/Closing_(morphology)
    # I regret getting into this
    # Applies morphological closing (cv2.MORPH_CLOSE), which fills small holes and connects nearby white regions.
    # This step helps in making QR codes more solid and connected for better contour detection.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)) # modify kernel in order to get better morphological closing
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours and filter for QR code
    # cv2.RETR_TREE retrieves all of the contours and reconstructs a full hierarchy of nested contours.
    # cv2.CHAIN_APPROX_SIMPLE reduces unnecessary points in the contour representation.
    cnts = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    # candidate contours
    candidates = []

    # Iterates through the detected contours.
    for c in cnts:
        # Use cv2.minAreaRect and cv2.boxPoints to get a tight rectangle with exactly 4 corner points.
        rect = cv2.minAreaRect(c)
        approx = cv2.boxPoints(rect)
        approx = np.int64(approx)

        # Extracts the bounding box
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            area = cv2.contourArea(c)
            ar = w / float(h)

            # possible qr codes
            if area <= 1000 or (ar < 0.7 or ar > 1.4):
                continue

            candidates.append((x, y, w, h))

    for (x, y, w, h) in candidates:
        candidate_roi = gray[y:y+h, x:x+w]

        if detect_version(candidate_roi) is not None:
            if draw_rectangle:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            return candidate_roi, image

    print("No QR code found.")
    return None, image


# Generalised resizing
def rescale_to_grid(image: np.array, grid_size: int) -> np.array:
    """
    Rescale the cropped image to a grid of the given size using nearest-neighbor.
    """
    im = Image.fromarray(image.astype(np.uint8))
    im_resized = im.resize((grid_size, grid_size), Image.NEAREST)
    return np.array(im_resized) > 128

def detect_version(image: np.array) -> int:
    """
    Try candidate versions (1–3) by rescaling and checking for three finder patterns.
    Returns the first matching version or None if not detected.
    """
    if image is None:
        return None
    for version in range(1, 4):
        grid_size = 21 + 4 * (version - 1)
        grid = rescale_to_grid(image, grid_size)

        if is_qr_code(grid):
            return version
    return None

def is_finder_pattern(block: np.array) -> bool:
    """
    Check if a 7x7 block matches the finder pattern.
    0 = black
    1 = white
    """
    if block.shape != (7, 7):
        return False
    expected = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ], dtype=bool)
    return np.array_equal(block, expected)

def detect_finder_patterns(matrix: np.array) -> np.array:
    """
    Slide a 7x7 window over the matrix to locate finder patterns.
    Returns a list with the center positions (row, col) of the found finder patterns.
    """
    positions = np.array([], dtype=int).reshape(0, 2)
    n = matrix.shape[0]
    for i in range(n - 6):
        for j in range(n - 6):
            block = matrix[i:i+7, j:j+7]
            if is_finder_pattern(block):
                positions = np.vstack([positions, [i+3, j+3]])

    return positions

def is_qr_code(matrix: np.array) -> bool:
    """
    Verify if the 3 finder patterns are located.
    """
    return len(detect_finder_patterns(matrix)) >= 1

# Fromat Segment
def extract_format_info(matrix: np.array) -> dict:
    """
    Read the 15 format information bits from fixed positions near the top-left finder.
    Unmask by XOR-ing with 0x5412.
    """
    coords = [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7),
              (8, 8),
              (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)]
    bits = 0
    for r, c in coords:
        bit = 0 if matrix[r, c] else 1 # 0 if pixel is white (True), 1 if it's black (False)
        bits = (bits << 1) | bit
    format_info = bits ^ 0x5412
    mask_pattern = (format_info >> 10) & 0b111
    ec_level_bits = (format_info >> 13) & 0b11
    ec_level = {0b01: 'L', 0b00: 'M', 0b11: 'Q', 0b10: 'H'}.get(ec_level_bits, 'L') # default: L
    return {'mask_pattern': mask_pattern, 'ec_level': ec_level}

def mask_condition(i: int, j: int, mask_pattern: int) -> bool:
    # Return True if the mask condition is met for the given mask pattern
    # taken from here https://commons.wikimedia.org/wiki/File:QR_Code_Mask_Patterns.svg
    # TODO: change to switch statement
    if mask_pattern in range(8):
        return constants.MASK_CONDITIONS[mask_pattern](i, j)
    return False

def get_reserved_mask(version: int, size: int) -> np.array:
    """
    Build a mask marking modules reserved for:
      - Finder patterns (and their separators)
      - Timing patterns (row 6 and column 6)
      - Format information areas (near the top-left finder)
      - Alignment patterns (for versions >= 2)
    """
    reserved = np.zeros((size, size), dtype=bool)
    # Finder patterns
    reserved[0:9, 0:9] = True           # top-left
    reserved[0:9, size-8:size] = True   # top-right
    reserved[size-8:size, 0:9] = True   # bottom-left

    # Timing patterns
    reserved[6, :] = True
    reserved[:, 6] = True

    # Format information areas (near top-left finder)
    reserved[8, 0:8] = True
    reserved[0:8, 8] = True

    # Alignment patterns (for versions >= 2)
    if version >= 2 and version in constants.ALIGNMENT_CENTERS:
        centers = constants.ALIGNMENT_CENTERS[version]
        for r in centers:
            for c in centers:
                # Skip if overlapping with finder patterns
                if (r < 9 and c < 9) or (r < 9 and c >= size - 8) or (r >= size - 8 and c < 9):
                    continue
                r0 = max(r - 2, 0)
                r1 = min(r + 3, size)
                c0 = max(c - 2, 0)
                c1 = min(c + 3, size)
                reserved[r0:r1, c0:c1] = True

    return reserved

def unmask_qr(matrix: np.array, mask_pattern: int, reserved: np.array) -> np.array:
    """
    Remove the data mask from non-reserved modules.
    """
    n = matrix.shape[0]
    unmasked = matrix.copy()
    for i in range(n):
        for j in range(n):
            if reserved[i, j]:
                continue
            if mask_condition(i, j, mask_pattern):
                unmasked[i, j] = not unmasked[i, j]
    return unmasked

def extract_data_bits(matrix: np.array, reserved: np.array) -> list:
    """
    Traverse the module matrix in the zigzag order to extract data bits.
    (This implementation iterates two columns at a time, skipping column 6.)
    """
    n = matrix.shape[0]
    bits = []
    col = n - 1
    upward = True
    while col > 0:
        if col == 6:  # Skip the timing pattern column
            col -= 1
        rows_range = range(n-1, -1, -1) if upward else range(n)
        for r in rows_range:
            for c in [col, col-1]:
                if not reserved[r, c]:
                    # black (False) → 1, white (True) → 0
                    bit = 0 if matrix[r, c] else 1
                    bits.append(bit)
        upward = not upward
        col -= 2
    return bits

def bits_to_bytes(bits: list) -> bytearray:
    """
    Group bits into 8-bit codewords.
    """
    # Ensure the number of bits is a multiple of 8 by padding with zeros
    while len(bits) % 8 != 0:
        bits.append(0)
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i+8]:
            byte = (byte << 1) | bit
        b.append(byte)
    return b

def decode_data(codewords: bytes) -> str:
    """
    Interpret the codewords.
    Supported modes:
        - Byte
        - Alphanumeric
        - Numeric
    """
    bit_str = ''.join(f'{byte:08b}' for byte in codewords)
    mode = bit_str[0:4]

    # Byte mode
    if mode == '0100':
        count = int(bit_str[4:12], 2) # the number of bytes in the message
        data_bits = bit_str[12:12 + count * 8]
        data = bytearray()
        for i in range(0, len(data_bits), 8):
            data.append(int(data_bits[i:i+8], 2))
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin1')

    # Alphanumeric mode
    elif mode == '0010':
        count = int(bit_str[4:13], 2) # char count
        table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:" # each alnum character is indexed in this table (0-44)
        result = ""
        bits_idx = 13
        while len(result) < count and bits_idx + 11 <= len(bit_str):
            num = int(bit_str[bits_idx:bits_idx+11], 2) # we read two characters simultaneously 45x45 = 2025 = aprox 2**11
            result += table[num // 45] + table[num % 45]
            bits_idx += 11
        return result[:count]

    # Numeric mode
    elif mode == '0001':
        count = int(bit_str[4:14], 2) # digit count
        result = ""
        bits_idx = 14
        """
        Each group of digits is encoded differently:
        3 digits → 10 bits
        2 digits → 7 bits
        1 digit → 4 bits
        """
        while len(result) < count and bits_idx < len(bit_str):
            remaining = count - len(result)
            if remaining >= 3 and bits_idx + 10 <= len(bit_str):
                num = int(bit_str[bits_idx:bits_idx+10], 2)
                result += f"{num:03d}"
                bits_idx += 10
            elif remaining == 2 and bits_idx + 7 <= len(bit_str):
                num = int(bit_str[bits_idx:bits_idx+7], 2)
                result += f"{num:02d}"
                bits_idx += 7
            elif remaining == 1 and bits_idx + 4 <= len(bit_str):
                num = int(bit_str[bits_idx:bits_idx+4], 2)
                result += f"{num}"
                bits_idx += 4
            else:
                break
        return result
    else:
        return "Unsupported mode"

def decode_qr_matrix(matrix: np.array, version: int) -> str:
    """
    Perform the full decoding.
    Args:
        module_matrix (list of list of int): The rescaled QR code matrix.
        version (int): The version of the QR code.
    Returns:
        decoded_data (str or bytes): The interpreted data from the QR code.
    """
    size = matrix.shape[0]
    reserved = get_reserved_mask(version, size)
    fmt = extract_format_info(matrix)
    mask_pattern = fmt['mask_pattern']
    unmasked_matrix = unmask_qr(matrix, mask_pattern, reserved)
    data_bits = extract_data_bits(unmasked_matrix, reserved)
    codewords = bits_to_bytes(data_bits)

    if version in constants.RS_PARAMS:
        expected_codewords, ecc_count = constants.RS_PARAMS[version]
    else:
        return "Unsupported version for RS parameters."

    # Use only the expected number of codewords
    codewords = codewords[:expected_codewords]

    try:
        rsc = RSCodec(ecc_count)
        decoded = rsc.decode(bytes(codewords))
        # tuple returned (decoded data, metadats)
        corrected = decoded[0]
    except ReedSolomonError as e:
        return "Error in RS decoding: " + str(e)

    return decode_data(corrected)

def full_decode(image: np.array) -> str:
    """
    Complete pipeline:
      - Read the image.
      - Crop to the QR region.
      - Detect the version.
      - Rescale to the appropriate grid.
      - Verify it appears to be a QR code.
      - Decode the QR matrix.
    """
    version = detect_version(image)
    if version is None:
        return "Could not detect QR code version."
    grid_size = 21 + 4 * (version - 1)
    module_matrix = rescale_to_grid(image, grid_size)
    if not is_qr_code(module_matrix):
        return "Not a valid QR code!"
    return decode_qr_matrix(module_matrix, version)
