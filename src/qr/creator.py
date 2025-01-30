from PIL import Image
import numpy as np

#macros
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
NEUTRAL = (60, 60, 60)

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
        #self.print_matrix()
        
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


#class to manage loading np_matrix in image
class QR_interface:
    def __init__(self, qr):
        self.qr = qr

        self.qr_size = 25
        self.img_size = 800
        self.module_size = self.img_size // self.qr_size

        self.img = Image.new('RGB', (self.img_size, self.img_size), WHITE)
        self.image_pixels = self.img.load()  

    def fill_module(self, row, col, color=BLACK):
        ms = self.module_size
        for i in range (col * ms, col * ms + ms):
            for j in range (row * ms, row * ms + ms):
                self.image_pixels[i,j] = color

    def write_image(self):
        matrix = self.qr.get_matrix()
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i][j] == 0:
                    self.fill_module(i, j, WHITE)
                elif matrix[i][j] == 1:
                    self.fill_module(i, j, BLACK)
                elif matrix[i][j] == 2:
                    self.fill_module(i, j, BLUE)
                elif matrix[i][j] == 3:
                    self.fill_module(i, j, RED)
                else:
                    self.fill_module(i, j, NEUTRAL)

    def save_image(self):
        self.write_image()
        self.img.show()
        self.img.save('encoded_qr.bmp', format=None)


def test():
    base = QR_base()
    
    interface = QR_interface(base)
    interface.save_image()

    encoder = Encoder('abcdefg')
    encoder.encode()

    # fiecare 10 pixeli reprezinta un punct
    # Create the pixel map
    # the quiet zone si patratele alea ca sa fie asezat

#     img = Image.new( 'RGB', (270,270), (0,0,0)) # Create a new black image
#     pixels = img.load()


#     # facem o functie care sa ne ajute sa desenam un block
#     # block(20, 24, (255,255,255))
#     def block(col, lin, culoare = (255,255,255), k=10):
#         for i in range (col*k, col*k+k):
#             for j in range (lin*k, lin*k+k):
#                 pixels[i,j] = culoare

#     def generate_finder_patterns():
#         img = Image.new('RGB', (270, 270), (0,0,0))

#         for j in range (img.size[0]):
#             for i in range(img.size[1]):
#                 if i < 10 or j < 10 or j > 259 or i > 259: # quiet zone
#                     pixels[i, j] = (255, 255, 255)
#                 if (i >= 20 and i < 30) and (j >= 20 and j < 60):
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 60 and i < 70 and j >= 20 and j < 70:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 70 and i < 80 and j >=10 and j < 80:
#                     pixels[i, j] = (0, 0, 0)
#                     pixels [j,i] = (0, 0, 0)
#                 if i >= 80 and i < 90 and j >= 10 and j < 90:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 20 and i < 30 and j >=210 and j < 250:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 60 and i < 70 and j >= 210 and j < 250:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 240 and i < 250 and j >= 30 and j < 60:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 200 and i < 210 and j >= 20 and j < 70:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i >= 180 and i < 190 and j>=10 and j < 90:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)
#                 if i>= 180 and i < 260 and j >= 80 and j < 90:
#                     pixels[i, j] = (255, 255, 255)
#                     pixels [j,i] = (255, 255, 255)

                
#     block(18,18, (0,0,0))
#     # timing strips
#     for i in range(8,19):
#         if i % 2 == 0:
#             block (7, i)
#             block(i, 7)
#         else:
#             block (7, i, (0,0,0))
#             block(i, 7,(0,0,0))


#     # data type
#     block (25, 25)
#     block (25,24)
#     block(24,24)
#     #number of characters in our code
#     # aici vom putea veni cu input mai incolo
#     test = str('www.youtube.com/veritasium')
#     lenw = bin(len(test))[2:]
#     while len(lenw) < 8:
#         lenw = '0' + lenw
#     # vom scrie o functie care sa scrie 8 biti in matrice
#     # pornind de la o pozitie data
#     def encoder(col_init, lin_init, ascii_code):
#         l = list(ascii_code)
#         l = [int(x) for x in l]
#         cnt = 0
#         for i in range(0, len(l), 2):
#             if l[i] == 0:
#                 block(col_init , lin_init-i//2)
#             else:
#                 block(col_init , lin_init-i//2,(0,0,0))
#             if l[i+1] == 0:
#                 block(col_init - 1, lin_init-i//2)
#             else:
#                 block(col_init - 1, lin_init-i//2,(0,0,0))
#     encoder(25,23,lenw)
#     # pana acum stim cum encodam si cate caractere va avea textul
#     # la inceput am facut totul negru si am pus doar alb
#     # acum vom completa si unde e cazul cu negru
#     # deoarece vrem sa vedem unde avem spatiu liber de completat
#     for i in range (27):
#         for j in range (27):
#             if j == 1 and i < 8 and i >= 1:
#                 block(j,i,(0,0,0))
#             if i == 1 and j >= 1 and j < 8:
#                 block(j,i,(0,0,0))
#             if j == 25 and i >= 1 and i < 8:
#                 block(i,j,(0,0,0))
#                 block(j,i,(0,0,0))
#             if i == 1 and j < 26 and j > 18:
#                 block(j,i,(0,0,0))
#                 block(i,j,(0,0,0))
#             if i == 7 and j < 26 and j > 18:
#                 block(j,i,(0,0,0))
#                 block(i,j,(0,0,0))
#             if j == 19 and i >= 1 and i < 8:
#                 block(i,j,(0,0,0))
#                 block(j,i,(0,0,0))
#             if i >= 3 and i <= 5 and ((j >= 3 and j <= 5) or (j <= 23 and j >= 21)):
#                 block(j,i,(0,0,0))
#             if j>= 3 and j <= 5 and i >= 21 and i <= 23:
#                 block(j,i,(0,0,0))
#     # facem rosii zonele de completat functionale ramase
#             if i == 9 and ((j >=1 and j <= 9) or (j <= 25 and j >=18)):
#                 block(j, i, (255,0,0))
#                 block(i,j,(255,0,0))
#     block(9,18,(0,0,0))
#     block(7,9,(0,0,0))
#     block(24,25,(0,0,0))
#     # in acest punct, spatiul gri este cel de completat
#     # si avem scrise formatarea si marimea
#     # trebuie encodat textul dat
#     # facem o fct care sa verifice daca un block este liber
#     def free(col, lin):
#         if pixels[col*10, lin*10] == (60,60,60):
#             return True
#         return False
#     def encore(text):
#         # va primi ca parametru textul
#         col = 25
#         lin = 19
#         cnt = 0
#         d = 1
#         blocat = 0
#         ascii_values = [format(ord(char), '08b') for char in text]
#         print (ascii_values)
#         # construieste pana la primul stop
#         # trebuie facut cazul cu
#         for i in ascii_values:
#             for litera in list(i):
#                 if free(col, lin):
#                     if litera == '0':
#                         block(col,lin)
#                     else:
#                         block(col,lin,(0,0,0))
#                     if cnt == 0:
#                         col -= 1
#                         cnt = 1
#                     else:
#                         lin -= d
#                         col += 1
#                         cnt = 0
#     encore(test)




#     # byte encoding
#     # aici primim textul care va fi string
#     # il convertim intr-o lista de ascii
#     img.show()

# #test()