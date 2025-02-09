from qr.visualizer import QR_Visualizer
from qr.builder import QRCodeBuilder
import qr.poly as poly

#class for encoding data
class Encoder:
    def __init__(self, message: str) -> None:
        self.message = message

        # max no. of data bits for our specification(2.M) = 28, 28*4=224
        self.max_data_bits = 224

    def generate_ecc(self) -> str:
        # For our specification(2.M), we have 16 ECC codewords
        poly.create_gf_tables()
        generator_polynomial = poly.gf_poly_gen(16)

        message = self.encode_data_string()
        message_polynomial = []
        for i in range(0, len(message) - 7, 8):
            bin_codeword = message[i:i + 8]
            coef = int(bin_codeword, 2)
            message_polynomial.append(coef)

        ecc = poly.gf_poly_div(message_polynomial + [0] * (len(generator_polynomial) - 1), generator_polynomial)
        ecc_bits = ''

        for nmb in ecc:
            bin_nmb = bin(nmb)[2:]
            while len(bin_nmb) < 8:
                bin_nmb = '0'+bin_nmb
            ecc_bits += bin_nmb
        return ecc_bits

    def encode_data_string(self) -> str:
        encoded = ''
        # mode: binary
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

def encode_text(text: str) -> None:
    base = QRCodeBuilder()
    encoder = Encoder(text)
    encoded_data = encoder.get_encoded()
    base.load_stream_in_qr(encoded_data)

    interface = QR_Visualizer(base)

    base.apply_best_mask()
    print(interface.qr_to_terminal())
    
    interface.save_image()
    print('QR Code saved as qr.png')


def generateQR(text: str) ->None:
    if len(text) >= 27:
        return None

    base = QRCodeBuilder()
    encoder = Encoder(text)

    encoded = encoder.get_encoded()
    base.load_stream_in_qr(encoded)
    mask = base.apply_best_mask()

    interface = QR_Visualizer(base)
    interface.save_image()

    res = {}
    res['mask'] = mask[0]
    res['mask-penalty'] = mask[1]
    return res

