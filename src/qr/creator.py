from PIL import Image
import numpy as np

#constants
PRIMITIVE_POLY = 0x11d


#class for encoding data
class Encoder:
    def __init__(self, message):
        self.message = message

        #tables for galois-field
        self.gf_exp, self.gf_log = [], []

        #max no. of data bits for our specification(2.M) = 28, 28*4=224
        self.max_data_bits = 224

    def create_gf_tables(self):
        #Fill the gf tables for exp and log
        self.gf_exp = [1] * 512
        self.gf_log = [0] * 256
        x = 1
        for i in range(255):
            self.gf_exp[i] = x
            self.gf_log[x] = i
            x <<= 1
            if x & 0x100:
                x ^= PRIMITIVE_POLY

        for i in range(255, 512):
            self.gf_exp[i] = self.gf_exp[i - 255]

    def gf_mult(self, x, y, primitive=PRIMITIVE_POLY, field_size=256):
        if x == 0 or y == 0:
            return 0
        return self.gf_exp[(self.gf_log[x] + self.gf_log[y]) % (field_size - 1)]
    
    def gf_poly_mult(self, p1, p2):
        #Multiply two gf polynomials
        res = [0] * (len(p1) + len(p2) - 1)
        for i in range(len(p1)):
            for j in range(len(p2)):
                res[i + j] ^= self.gf_mult(p1[i], p2[j])
        return res
    
    def gf_poly_gen(self, degree):
        #Generate the generator polynomial
        gen = [1]
        for i in range(degree):
            gen = self.gf_poly_mult(gen, [1, self.gf_exp[i]])
        return gen

    def gf_poly_div(self, dividend, divisor):
        #Performs polynomial division in GF(2^8). Returns quotient and remainder.
        msg_out = list(dividend)
        divisor_degree = len(divisor) - 1
        
        for i in range(len(dividend) - divisor_degree):
            coef = msg_out[i]
            if coef != 0:
                for j in range(len(divisor)):
                    msg_out[i + j] ^= self.gf_mult(divisor[j], coef)
        
        remainder = msg_out[-divisor_degree:]
        return remainder

    def generate_ecc(self):
        #For our specification(2.M), we have 16 ECC codewords
        self.create_gf_tables()
        generator_polynomial = self.gf_poly_gen(16)

        message = self.encode_data_string()
        message_polynomial = []
        for i in range(0, len(message)-7, 8):
            bin_codeword = message[i:i+8] 
            coef = int(bin_codeword, 2)
            message_polynomial.append(coef)

        ecc = self.gf_poly_div(message_polynomial + [0]*(len(generator_polynomial)-1), generator_polynomial)
        ecc_bits = ''

        for nmb in ecc:
            bin_nmb = bin(nmb)[2:]
            while len(bin_nmb) < 8:
                bin_nmb = '0'+bin_nmb
            ecc_bits += bin_nmb
        return ecc_bits

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
        return self.encode_data_string() + self.generate_ecc() + '0'*7
        

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

    def load_stream_in_qr(self, data: str) -> None:
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

            #print(f'Filling group: {group_idx}, and col_idx at {col_idx}')

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

    def apply_mask(self, mask_idx:int) -> None:
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
        
    def mask1(self)-> None:
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

    def mask2(self)-> None:
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

    def mask3(self)-> None:
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

    def mask4(self)-> None:
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

    def mask5(self)-> None:
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

    def mask6(self)-> None:
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

    def mask7(self)-> None:
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

    def mask8(self)-> None:
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

    def apply_format_info(self, format_string: str)-> None:
        if len(format_string) != 15: 
            print('Invalid format string!')
            return
        format_string = list(format_string)
        for i in range(len(format_string)):
            format_string[i] = int(format_string[i])
            if format_string[i] == 1:
                format_string[i] = 0
            else:
                format_string[i] = 1
        self.qr_matrix[8, 0] = format_string[0]
        self.qr_matrix[8, 1] = format_string[1]
        self.qr_matrix[8, 2] = format_string[2]
        self.qr_matrix[8, 3] = format_string[3]
        self.qr_matrix[8, 4] = format_string[4]
        self.qr_matrix[8, 5] = format_string[5]
        self.qr_matrix[8, 7] = format_string[6]
        self.qr_matrix[8, 8] = format_string[7]
        self.qr_matrix[7, 8] = format_string[8]
        self.qr_matrix[5, 8] = format_string[9]
        self.qr_matrix[4, 8] = format_string[10]
        self.qr_matrix[3, 8] = format_string[11]
        self.qr_matrix[2, 8] = format_string[12]
        self.qr_matrix[1, 8] = format_string[13]
        self.qr_matrix[0, 8] = format_string[14]

        self.qr_matrix[24, 8] = format_string[0]
        self.qr_matrix[23, 8] = format_string[1]
        self.qr_matrix[22, 8] = format_string[2]
        self.qr_matrix[21, 8] = format_string[3]
        self.qr_matrix[20, 8] = format_string[4]
        self.qr_matrix[19, 8] = format_string[5]
        self.qr_matrix[18, 8] = format_string[6]
        self.qr_matrix[8, 17] = format_string[7]
        self.qr_matrix[8, 18] = format_string[8]
        self.qr_matrix[8, 19] = format_string[9]
        self.qr_matrix[8, 20] = format_string[10]
        self.qr_matrix[8, 21] = format_string[11]
        self.qr_matrix[8, 22] = format_string[12]
        self.qr_matrix[8, 23] = format_string[13]
        self.qr_matrix[8, 24] = format_string[14]

    def get_matrix(self) -> np.array:
        return self.qr_matrix
    
    
from qr.visualizer import QR_Visualizer
def test():
    base = QR_base()
    encoder = Encoder('testQRWorking')
    encoded_data = encoder.get_encoded()
    base.load_stream_in_qr(encoded_data)

    interface = QR_Visualizer(base)

    #for now apply mask 1 and format info for mask 1
    base.apply_mask(1)  
    base.apply_format_info('101010000010010')

    interface.save_image()
    