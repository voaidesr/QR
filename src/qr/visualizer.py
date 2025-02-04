from PIL import Image
from qr.encoder import QR_base
import random

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
NEUTRAL = (60, 60, 60)

class QR_Visualizer:
    def __init__(self, qr: QR_base):
        self.qr = qr

        self.qr_size: int = 25
        self.img_size: int = 800
        self.module_size: int = self.img_size // self.qr_size

        self.img: Image.Image = Image.new('RGB', (self.img_size, self.img_size), WHITE)
        self.image_pixels = self.img.load()

    def fill_module(self, row: int, col: int, color=BLACK) -> None:
        ms = self.module_size
        for i in range(col * ms, col * ms + ms):
            for j in range(row * ms, row * ms + ms):
                self.image_pixels[i, j] = color

    def write_image(self) -> None:
        matrix = self.qr.get_matrix()
        for i in range(25):
            for j in range(25):
                color_map = {0: BLACK, 1: WHITE, 2: BLUE, 3: RED, 4: NEUTRAL}
                color = color_map.get(matrix[i][j])
                self.fill_module(i, j, color)

    def show_image(self) -> None:
        self.write_image()
        self.img.show()

    def save_image(self, filename: str = 'qr_code.png', format: str = 'PNG') -> None:
        self.write_image()
        self.img.save(filename, format=format)
