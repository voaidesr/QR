import os 

# Project root (for file paths)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# RS parameters for error correction level L, versions 1-3
RS_PARAMS = {
    1: (26, 7),
    2: (44, 10),
    3: (70, 15)
}

# Alignment pattern centers for versions 2 to 3
ALIGNMENT_CENTERS = {
    2: [6, 18],
    3: [6, 22]
}

# Format string for error correction
FORMAT_STRING = {
    0: '101010000010010',
    1: '101000100100101',
    2: '101111001111100',
    3: '101101101001011',
    4: '100010111111001',
    5: '100000011001110',
    6: '100111110010111',
    7: '100101010100000'
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
NEUTRAL = (60, 60, 60)

# Mask conditions
MASK_CONDITIONS = {
        0: lambda i, j: (i + j) % 2 == 0,
        1: lambda i, j: i % 2 == 0,
        2: lambda i, j: j % 3 == 0,
        3: lambda i, j: (i + j) % 3 == 0,
        4: lambda i, j: ((i // 2 + j // 3) % 2) == 0,
        5: lambda i, j: (((i * j) % 2) + ((i * j) % 3)) == 0,
        6: lambda i, j: ((((i * j) % 2) + ((i * j) % 3)) % 2) == 0,
        7: lambda i, j: ((((i + j) % 2) + ((i * j) % 3)) % 2) == 0,
}