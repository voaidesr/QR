from PIL import Image
# fiecare 10 pixeli reprezinta un punct
img = Image.new( 'RGB', (270,270), (60,60,60)) # Create a new black image
pixels = img.load() # Create the pixel map
# the quiet zone si patratele alea ca sa fie asezat
for j in range (img.size[0]):
    for i in range(img.size[1]):
        if i < 10 or j < 10 or j > 259 or i > 259: # quiet zone
            pixels[i, j] = (255, 255, 255)
        if (i >= 20 and i < 30) and (j >= 20 and j < 60): 
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 60 and i < 70 and j >= 20 and j < 70:
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 70 and i < 80 and j >=10 and j < 80:
            pixels[i, j] = (0, 0, 0)
            pixels [j,i] = (0, 0, 0)
        if i >= 80 and i < 90 and j >= 10 and j < 90:
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 20 and i < 30 and j >=210 and j < 250:
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 60 and i < 70 and j >= 210 and j < 250:
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 240 and i < 250 and j >= 30 and j < 60: 
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 200 and i < 210 and j >= 20 and j < 70: 
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i >= 180 and i < 190 and j>=10 and j < 90: 
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
        if i>= 180 and i < 260 and j >= 80 and j < 90:
            pixels[i, j] = (255, 255, 255)
            pixels [j,i] = (255, 255, 255)
# facem o functie care sa ne ajute sa desenam un block
def block(col, lin, culoare = (255,255,255)):
    k = 10
    for i in range (col*k, col*k+k):
        for j in range (lin*k, lin*k+k):
            pixels[i,j] = culoare
# block(20, 24, (255,255,255))
for i in range (17,20):
    for j in range(17,20):
        block(i,j)
block(18,18, (0,0,0))
# timing strips
for i in range(8,19):
    if i % 2 == 0:
        block (7, i)
        block(i, 7)
    else:
        block (7, i, (0,0,0))
        block(i, 7,(0,0,0))
# data type 
block (25, 25)
block (25,24)
block(24,24)
#number of characters in our code
# aici vom putea veni cu input mai incolo
test = str('www.youtube.com/veritasium')
lenw = bin(len(test))[2:]
while len(lenw) < 8:
    lenw = '0' + lenw
# vom scrie o functie care sa scrie 8 biti in matrice
# pornind de la o pozitie data
def encoder(col_init, lin_init, ascii_code):
    l = list(ascii_code)
    l = [int(x) for x in l]
    cnt = 0
    for i in range(0, len(l), 2):
        if l[i] == 0:
            block(col_init , lin_init-i//2)
        else:
            block(col_init , lin_init-i//2,(0,0,0))
        if l[i+1] == 0:
            block(col_init - 1, lin_init-i//2)
        else:
            block(col_init - 1, lin_init-i//2,(0,0,0))
encoder(25,23,lenw)
# pana acum stim cum encodam si cate caractere va avea textul
# la inceput am facut totul negru si am pus doar alb
# acum vom completa si unde e cazul cu negru
# deoarece vrem sa vedem unde avem spatiu liber de completat
for i in range (27):
    for j in range (27):
        if j == 1 and i < 8 and i >= 1:
            block(j,i,(0,0,0))
        if i == 1 and j >= 1 and j < 8:
            block(j,i,(0,0,0))
        if j == 25 and i >= 1 and i < 8:
            block(i,j,(0,0,0))
            block(j,i,(0,0,0))
        if i == 1 and j < 26 and j > 18:
            block(j,i,(0,0,0))
            block(i,j,(0,0,0))
        if i == 7 and j < 26 and j > 18:
            block(j,i,(0,0,0))
            block(i,j,(0,0,0))
        if j == 19 and i >= 1 and i < 8:
            block(i,j,(0,0,0))
            block(j,i,(0,0,0))
        if i >= 3 and i <= 5 and ((j >= 3 and j <= 5) or (j <= 23 and j >= 21)):
            block(j,i,(0,0,0))
        if j>= 3 and j <= 5 and i >= 21 and i <= 23:
            block(j,i,(0,0,0))
# facem rosii zonele de completat functionale ramase
        if i == 9 and ((j >=1 and j <= 9) or (j <= 25 and j >=18)):
            block(j, i, (255,0,0))
            block(i,j,(255,0,0))
block(9,18,(0,0,0))
block(7,9,(0,0,0))
block(24,25,(0,0,0))
# in acest punct, spatiul gri este cel de completat
# si avem scrise formatarea si marimea
# trebuie encodat textul dat
# facem o fct care sa verifice daca un block este liber
def free(col, lin):
    if pixels[col*10, lin*10] == (60,60,60):
        return True
    return False
def encore(text):
    # va primi ca parametru textul
    col = 25
    lin = 19
    cnt = 0
    d = 1
    blocat = 0
    ascii_values = [format(ord(char), '08b') for char in text]
    print (ascii_values)
    # construieste pana la primul stop
    # trebuie facut cazul cu 
    for i in ascii_values:
        for litera in list(i):
            if free(col, lin):
                if litera == '0':
                    block(col,lin)
                else:
                    block(col,lin,(0,0,0))
                if cnt == 0:
                    col -= 1
                    cnt = 1
                else:
                    lin -= d
                    col += 1
                    cnt = 0
encore(test)

        


# byte encoding
# aici primim textul care va fi string
# il convertim intr-o lista de ascii
img.show()
