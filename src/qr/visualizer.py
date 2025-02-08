from PIL import Image
from qr.builder import QRCodeBuilder
import qr.constants as constants

class QR_Visualizer:
    def __init__(self, qr: QRCodeBuilder):
        self.qr = qr

        self.qr_size: int = 27
        self.img_size: int = 864
        self.module_size: int = self.img_size // self.qr_size

        self.img: Image.Image = Image.new('RGB', (self.img_size, self.img_size), constants.WHITE)
        self.image_pixels = self.img.load()

    def fill_module(self, row: int, col: int, color=constants.BLACK) -> None:
        ms = self.module_size
        for i in range(col * ms, col * ms + ms):
            for j in range(row * ms, row * ms + ms):
                self.image_pixels[i, j] = color

    def write_image(self) -> None:
        matrix = self.qr.get_matrix()
        for i in range(26):
            for j in range(26):
                self.fill_module(i, j, (255, 255, 255))
        for i in range(1,26):
            for j in range(1, 26):
                color_map = {0: constants.BLACK, 1: constants.WHITE, 2: constants.BLUE, 3: constants.RED, 4: constants.NEUTRAL}
                color = color_map.get(matrix[i-1][j-1])
                self.fill_module(i, j, color)

    def show_image(self) -> None:
        self.write_image()
        self.img.show()

    def save_image(self, filename: str = 'qr_code.png', format: str = 'PNG') -> None:
        self.write_image()
        self.img.save(filename, format=format)
