from PIL import Image
import numpy as np

#class for encoding data
class Encoder:
    def __init__(self, message):
        self.message = message
        self.encoded = ''

    def encode(self):
        #mode: binary   
        mode = '0100'

        #size of message
        char_count = bin(len(self.message))[2:]
        while len(char_count) < 8:
            char_count = '0' + char_count

        #data bits
        for ch in self.message:
            print(bin(ord(ch)))


        self.encoded += mode + char_count
        print(self.encoded)

#class that manages loading data streams into qr
class QR_base:
    def __init__(self):
        self.qr_matrix = np.zeros((25, 25), dtype=int)
        self.qr_matrix[2,3] = 1

        self.fill_finder_patterns()

    def __init__(self, matrix: np.array):
        self.qr_matrix = matrix
        
    def fill_finder_patterns(self):
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                self.qr_matrix[i,j] = int(val)
                j += 1
            i += 1

    def print_matrix(self):
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                print(self.qr_matrix[i, j], end=" ") 
            print() 

    def get_matrix(self):
        return self.qr_matrix


from qr.visualizer import QR_Visualizer

def test():
    base = QR_base()
    
    interface = QR_Visualizer(base)
    interface.save_image()

    encoder = Encoder('abcdefg')
    encoder.encode()