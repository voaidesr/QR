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

        while ch_idx < data_length and group_idx <= 12:
            if group_idx == 9:
                # at this group we encounter the vertical timing pattern. Here we skip 1 column:
                col_idx -= 1 

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
    def apply_mask(self, mask_idx:int):

        if mask_idx == 1:
            self.mask1()
        elif mask_idx == 2:
            self.mask2()
        elif mask_idx == 3:
            self.mask3()
        elif mask_idx == 4:
            self.mask4()
        elif mask_idx == 5:
            self.mask5()
        elif mask_idx == 6:
            self.mask6()
        elif mask_idx == 7:
            self.mask7()
        elif mask_idx == 8:
            self.mask8()
        
    def mask1(self):
            a = np.zeros((25,25), dtype=int)
            f = open('./res/function_patterns.txt')
            i = 0
            for line in f.readlines():
                j = 0
                for val in line.split():
                    a[i,j] = int(val)
                    j += 1
                i += 1
            # Iterate through matrix
            for i in range(self.qr_matrix.shape[0]):
                for j in range(self.qr_matrix.shape[1]):
                    if self.qr_matrix[i,j] in [0,1] and (i + j) % 2 == 0 and a[i,j] == 4:
                        self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
            self.qr_matrix[8,2] = 0
            self.qr_matrix[8,3] = 1
            self.qr_matrix[8,4] = 0
            self.qr_matrix[22,8] = 0
            self.qr_matrix[21,8] = 1
            self.qr_matrix[20,8] = 0
    def mask2(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and j % 2 == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
            self.qr_matrix[8,2] = 0
            self.qr_matrix[8,3] = 1
            self.qr_matrix[8,4] = 1
            self.qr_matrix[22,8] = 0
            self.qr_matrix[21,8] = 1
            self.qr_matrix[20,8] = 1
    def mask3(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and j % 3 == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
        self.qr_matrix[8,2] = 0
        self.qr_matrix[8,3] = 0
        self.qr_matrix[8,4] = 0
        self.qr_matrix[22,8] = 0
        self.qr_matrix[21,8] = 0
        self.qr_matrix[20,8] = 0
    def mask4(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and (i+j) % 3 == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
        self.qr_matrix[8,2] = 0
        self.qr_matrix[8,3] = 0
        self.qr_matrix[8,4] = 1
        self.qr_matrix[22,8] = 0
        self.qr_matrix[21,8] = 0
        self.qr_matrix[20,8] = 1
    def mask5(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and ((int(i/2) + int(j/3)) % 2) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
        self.qr_matrix[8,2] = 1
        self.qr_matrix[8,3] = 1
        self.qr_matrix[8,4] = 0
        self.qr_matrix[22,8] = 1
        self.qr_matrix[21,8] = 1
        self.qr_matrix[20,8] = 0
    def mask6(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and (((i*j) % 2) + ((i*j) % 3)) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
        self.qr_matrix[8,2] = 1
        self.qr_matrix[8,3] = 1
        self.qr_matrix[8,4] = 1
        self.qr_matrix[22,8] = 1
        self.qr_matrix[21,8] = 1
        self.qr_matrix[20,8] = 1
    def mask7(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and ((((i*j) % 2) + ((i*j) % 3))%2) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
        self.qr_matrix[8,2] = 1
        self.qr_matrix[8,3] = 0
        self.qr_matrix[8,4] = 0
        self.qr_matrix[22,8] = 1
        self.qr_matrix[21,8] = 0
        self.qr_matrix[20,8] = 0
    def mask8(self):
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and (((i+j) % 2) + ((i*j) % 3)) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]
        self.qr_matrix[8,2] = 1
        self.qr_matrix[8,3] = 0
        self.qr_matrix[8,4] = 1
        self.qr_matrix[22,8] = 1
        self.qr_matrix[21,8] = 0
        self.qr_matrix[20,8] = 1
    def get_matrix(self) -> np.array:
        return self.qr_matrix
    
    
from qr.visualizer import QR_Visualizer
def test():
    base = QR_base(np.zeros((25,25)))

    encoder = Encoder('www.youtube.com/veritasium')
    e = encoder.get_encoded()

    base.load_stream_in_qr(e)

    base.apply_mask(2)
    

    interface = QR_Visualizer(base)
    interface.save_image()
