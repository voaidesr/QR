from PIL import Image
import numpy as np

#class for encoding data
class Encoder:
    def __init__(self, message):
        self.message = message

        #max no. of data bits for our specification = v.2(M err. correct.) 28, 28*4=224
        self.max_data_bits = 224

    def encode_data_string(self) -> str:
        encoded = ''
        #mode: binary   
        mode = '0100'

        #size of message
        char_count = bin(len(self.message))[2:]
        while len(char_count) < 8:
            char_count = '0' + char_count

        #data bits
        databits = ''
        for ch in self.message:
            ch_byte = bin(ord(ch))[2:]
            while len(ch_byte) < 8:
                ch_byte = '0' + ch_byte
            databits += ch_byte

        encoded += mode + char_count + databits

        if len(encoded) > self.max_data_bits:
            #cannot encode data
            print('Cannot encode data! Data string too large!')
            return ''
        
        #add terminator
        diff = self.max_data_bits - len(encoded)
        if diff > 4:
            encoded += '0' * 4
            r = len(encoded) % 8
            if r % 8 != 0:
                encoded += '0' * (8 - r)

            #add pad bytes
            if len(encoded) < self.max_data_bits:
                pads = ['11101100', '00010001']
                i = 0
                while len(encoded) < self.max_data_bits:
                    encoded += pads[i]
                    i = (i+1) % 2
        else:
            encoded += '0' * diff
        return encoded
    
    def get_encoded(self) -> str:
        return self.encode_data_string()
        

#class that manages loading data streams into qr
class QR_base:
    def __init__(self, matrix: np.array = np.zeros((25,25), dtype=int)):
        self.qr_matrix = matrix
        self.fill_finder_patterns()
        
    def fill_finder_patterns(self) -> None:
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                self.qr_matrix[i,j] = int(val)
                j += 1
            i += 1

    def print_matrix(self) -> None:
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                print(self.qr_matrix[i, j], end=" ") 
            print() 

    def load_stream_in_qr(self, data: str):
        matrix = self.qr_matrix
        n = 25

        data = list(data)
        for i in range(len(data)):
            if data[i] == '1':
                data[i] = 0
            else:
                data[i] = 1
        
        group_idx, col_idx, ch_idx = 0, 24, 0
        data_length = len(data)
        print(data_length)

        while ch_idx < data_length and group_idx <= 12:
            print(f'Filling group: {group_idx}, and col_idx at {col_idx}, and pos in data: {ch_idx}')
            if group_idx % 2 == 0:
                #fill from bottom to top
                for line in range(n-1, -1, -1):
                    el_r = matrix[line, col_idx]
                    el_l = matrix[line, col_idx-1] if col_idx-1 >= 0 else -1

                    if el_r == 4:
                        #it is not reserved
                        matrix[line, col_idx] = data[ch_idx]
                        ch_idx += 1
                    
                    if ch_idx >= data_length:
                        break

                    if el_l == 4:
                        #it is not reserved
                        matrix[line, col_idx-1] = data[ch_idx]
                        ch_idx += 1
                col_idx -= 2
            else:
                #fill from top to bottom
                for line in range(0, n):
                    el_r = matrix[line][col_idx]
                    el_l = matrix[line, col_idx-1] if col_idx-1 >= 0 else -1
                    if el_r == 4:
                        #it is not reserved
                        matrix[line, col_idx] = data[ch_idx]
                        ch_idx += 1
                    
                    if ch_idx >= data_length:
                        break

                    if el_l == 4:
                        #it is not reserved
                        matrix[line, col_idx-1] = data[ch_idx]
                        ch_idx += 1
                col_idx -= 2

            if ch_idx >= data_length:
                break

            group_idx += 1



    def get_matrix(self) -> np.array:
        return self.qr_matrix
    
    
from qr.visualizer import QR_Visualizer
def test():
    base = QR_base(np.zeros((25,25)))

    encoder = Encoder('Hello, World!')
    e = encoder.get_encoded()
    print(e)

    base.load_stream_in_qr(e)

    interface = QR_Visualizer(base)
    interface.save_image()

    # print(e[0:4])
    # print(e[4:12])
    # i = 12
    # while i+8 < 232:
    #     print(e[i:i+8])
    #     i += 8
    