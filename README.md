# QR code encoder/decoder

## Team:
Get Muxed  
  
Members:
- Robu Petru Razvan, 152
- Aioanei Florin, 151
- Verzotti Matteo, 151
- Voaides-Negustor Robert, 151


## Project description

When working on this project we chose to split the work in two equal parts: encoder and decoder.
### Encoder
1. Team members
    - Encoder Team: **Aioanei Florin** and **Robu Petru Razvan**
2. Details: 
    - Used the *Image* library in *Pillow* for generating and working with images in general. The encoder makes use of a standard matrix, which is then transposed in to a png file.
    - Used *Numpy* for working with matrix. The QR code is represented as a 25x25 matrix of integer values. Each value represents a state of the respective QR module (reserved, white, black, not-yet-colored).
    - The encoder uses *Reed-Solomon* error correction. The Reed-Solomon error correction uses polynomial divisions with polynomials that have coeficients in a *Galois Field* (GF256). Our algorithm generates the tables with values for exponents and logarithms of galois field numbers and uses the tables when doing the polynomial division.
    - The Reed-Solomon error correction algorithm makes use of a *generator polynomial*. The generator polynomial could be hardcoded, because it depends on the number of ecc codewords our QR requires (which is fixed), but our algorithm generates the polynomial recursively.
    - The QR code standard specifies *8 masks* that can be applied to the qr code. A mask is an operation that can be applied to the code in pursuit of making it better for interpretation and scanning. Depending on the mask number, there occurs a transformation on the matrix and then the new code is given a penalty score. Our encoder does this as well, it evaluates every mask and determines the *best one*.
3. Resources
   - A great resource and aid during this project was: [Thonky's QR Code Tutorial](https://www.thonky.com/qr-code-tutorial/).
   - Another great tool was the [step-by-step QR code creator](https://www.nayuki.io/page/creating-a-qr-code-step-by-step). This enabled us to find our mistakes and debug the application easily.
   - Another sources include the wikipedia articles on [QR codes](https://en.wikipedia.org/wiki/QR_code) and [Reed-Solomon Error Correction](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)

### Decoder
1. Team members:
   - Decoder Team: **Verzotti Matteo** and **Voaides-Negustor Robert**
2. Details:
   - Used the *OpenCV* library (cv2) for image preprocessing, edge detection, and QR code isolation. The decoder applies multiple image processing techniques:
        - *Edge Detection*: Detects sharp transitions in pixel intensity to outline the QR code. This helps in separating the QR from the background, even in noisy images.
        - *Thresholding and Morphological Operations*: Converts the image into a binary format and enhances the QR code structure for better contour detection.
    - The edge detection step is crucial for cropping the QR code accurately. Once edges are detected, the algorithm identifies the contours and extracts the Region of Interest (ROI), ensuring the QR code is isolated correctly before decoding.
    - Used *NumPy* for matrix operations. The extracted QR code is processed as a binary matrix, where each module (QR pixel) is represented as either white or black.
    - Implemented a QR version detection algorithm, which identifies the QR version (1–3) by detecting the three finder patterns and analyzing the module grid size.
    - The decoder identifies the format information from predefined locations in the QR matrix. It extracts error correction level and mask pattern, unmasking the QR code before proceeding with data extraction.
    - Used *Reed-Solomon* error correction through the reedsolo library. The algorithm applies polynomial division in a Galois Field (GF256) to correct potential errors in the QR code. The reedsolo library is specifically used to decode and correct the QR code data by handling error correction codewords.
    - Extracts and interprets encoded data by reading codewords in zigzag order. The decoder supports byte mode, alphanumeric mode, and numeric mode by parsing and converting bit sequences accordingly.
3. Resources:
    - This interactive explanation: [QR codes - a visual explanation | a(mod m)](https://amodm.com/blog/2024/05/28/qr-codes-a-visual-explainer)
    - The decoder uses a method of detecting qr codes using openCV inspired by [nathancy](https://stackoverflow.com/users/11162165/nathancy). The original model has been developed and improved in order to better fit the project. 
    - Mask pattern rules [QR Code Mask Patterns](https://commons.wikimedia.org/wiki/File:QR_Code_Mask_Patterns.svg)
### GUI
1. Details about the UI of our application:
    - In the encoder section, you can write your own data string and generate a qr code with it. We have also included some buttons to easily load our team name and the ASC course website link.
    - In the decoder section, you can upload an image of a qr code and the decoder will get the data it contains. There is also the option to check the image recognition part of the algorithm.


## Preview
![Screenshot from 2025-02-03 17-10-16](https://github.com/user-attachments/assets/a245dee3-b46f-4b80-8245-a45cafebadad)


## Setup
This project follows a structured setup using *Poetry* for dependency management and virtual environment handling.

### Installing Poetry 
Poetry is required to manage dependencies and run the project. If Poetry is not installed, follow the official installation [guide.](https://python-poetry.org/docs/)  
Alternatively, you can install Poetry using the following command:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```  
### Running Prerequisites
Before running the project, ensure you have the following installed:
- Python 3.8 or higher
- Poetry (see installation guide above)  

Navigate to the project directory and install the required dependencies:
```bash
poetry install
```
This will create a virtual environment and install all dependencies specified in the pyproject.toml file.

### Running the Project
To execute the project, use the following command structure:
```bash
poetry run qr [COMMAND]
``` 
#### Available Commands  
Encode a QR Code:
```bash
poetry run qr encode [text_to_encode]
```  
This receives a string as an argument, saves the encoded tring as a QR code at QR/src/qr and shows the QR image in the terminal.  

Decode a QR Code:
```bash
poetry run qr decode  [path_to_QR]
```  
This receives a path to an image which the program tries to decode. If it is not a QR code, the program will return an error, otherwise, the text that has been decoded from the QR will be shown in the terminal.  

Run the GUI Application:
```bash
poetry run qr gui
```  
Ensure you are in the project directory before running these commands.




