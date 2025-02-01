import numpy as np
from PIL import Image
from reedsolo import RSCodec, ReedSolomonError

# RS parameters for error correction level L, versions 1-3
rs_params = {
    1: (26, 7),
    2: (44, 10),
    3: (70, 15)
}

# Alignment pattern centers for versions 2 to 3
alignment_centers = {
    2: [6, 18],
    3: [6, 22]
}

def read_qr(image_path: str) -> np.array:
    """
    Decodes an image to a boolean NumPy array.

    Parameters:
    image_path (str): The path to the image file.
    """
    im = Image.open(image_path).convert('RGB') # Ensure it's in RGB mode
    np_array = np.array(im)
    
    # Convert rgb values to True and False
    return np.all(np_array == [255, 255, 255], axis=-1) 

# TODO: In the future, fina a way to make this function more robust
#       for example, the case where the code can be surrounded by black pixels
def crop_qr(image: np.array) -> np.array:
    """
    Crop extra white space around the QR code.
    """
    rows = np.any(~image, axis=1)
    cols = np.any(~image, axis=0)
    if not np.any(rows) or not np.any(cols):
        return image  # Nothing to crop
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return image[rmin:rmax+1, cmin:cmax+1]

# Generalised resizing
def rescale_to_grid(image: np.array, grid_size: int) -> np.array:
    """
    Rescale the cropped image to a grid of the given size using nearest-neighbor.
    """
    im = Image.fromarray(image.astype(np.uint8) * 255)
    im_resized = im.resize((grid_size, grid_size), Image.NEAREST)
    return np.array(im_resized) > 128

def detect_version(image: np.array) -> int:
    """
    Try candidate versions (1–3) by rescaling and checking for three finder patterns.
    Returns the first matching version or None if not detected.
    """
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

def detect_finder_patterns(matrix: np.array):
    """
    Slide a 7x7 window over the matrix to locate finder patterns.
    Returns a list with the center positions (row, col) of the found finder patterns.
    """
    positions = []
    n = matrix.shape[0]
    for i in range(n - 6):
        for j in range(n - 6):
            block = matrix[i:i+7, j:j+7]
            if is_finder_pattern(block):
                positions.append((i + 3, j + 3))
    return positions

def is_qr_code(matrix: np.array) -> bool:
    """
    Verify if the 3 finder patterns are located.
    """
    return len(detect_finder_patterns(matrix)) == 3

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
    if mask_pattern == 0:
        return (i + j) % 2 == 0
    elif mask_pattern == 1:
        return i % 2 == 0 
    elif mask_pattern == 2:
        return j % 3 == 0
    elif mask_pattern == 3:
        return (i + j) % 3 == 0
    elif mask_pattern == 4:
        return ((i // 2) + (j // 3)) % 2 == 0
    elif mask_pattern == 5:
        return (i * j) % 2 + (i * j) % 3 == 0
    elif mask_pattern == 6:
        return ((i * j) % 2 + (i * j) % 3) % 2 == 0
    elif mask_pattern == 7:
        return ((i + j) % 2 + (i * j) % 3) % 2 == 0
    else:
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
    if version >= 2 and version in alignment_centers:
        centers = alignment_centers[version]
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
    
    if version in rs_params:
        expected_codewords, ecc_count = rs_params[version]
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

def full_decode(image_path: str) -> str:
    """
    Complete pipeline:
      - Read the image.
      - Crop to the QR region.
      - Detect the version.
      - Rescale to the appropriate grid.
      - Verify it appears to be a QR code.
      - Decode the QR matrix.
    """
    raw = read_qr(image_path)
    cropped = crop_qr(raw)
    version = detect_version(cropped)
    if version is None:
        return "Could not detect QR code version."
    grid_size = 21 + 4 * (version - 1)
    module_matrix = rescale_to_grid(cropped, grid_size)
    if not is_qr_code(module_matrix):
        return "Not a valid QR code!"
    return decode_qr_matrix(module_matrix, version)
