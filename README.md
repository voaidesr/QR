# QR

## Setup

Used the tutorial [here](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/) to set up the project.

## Running Prerequisites

Before running the project, ensure you have the following prerequisites installed:

- Python 3.8 or higher
- poetry

To install the required dependencies, run the following command:

```sh
poetry install
```

This will create a virtual environment and install all the dependencies specified in the `pyproject.toml` file.

## Running the Project

To run the project, use the following command:

```sh
poetry run qr [COMMAND]
```

To run the GUI version of the application use:
```sh
poetry run qr gui
```

## Preview
![Screenshot from 2025-02-03 17-10-16](https://github.com/user-attachments/assets/a245dee3-b46f-4b80-8245-a45cafebadad)


## Notes

1. Encoder
    - Used the `Image` library in `Pillow` for generating and working with images in general. The encoder makes use of a standard matrix, which is then transposed in to a png file.
    - Used `Numpy` for working with matrix. The QR code is represented as a 25x25 matrix of integer values. Each value represents a state of the respective QR module (reserved, white, black, not-yet-colored).
    - The encoder uses `Reed-Solomon` error correction. The Reed-Solomon error correction uses polynomial divisions with polynomials that have coeficients in a `Galois Field` (GF256). Our algorithm generates the tables with values for exponents and logarithms of galois field numbers and uses the tables when doing the polynomial division.
    - The Reed-Solomon error correction algorithm makes use of a `generator polynomial`. The generator polynomial could be hardcoded, because it depends on the number of ecc codewords our QR requires (which is fixed), but our algorithm generates the polynomial recursively.
    - The QR code standard specifies `8 masks` that can be applied to the qr code. A mask is an operation that can be applied to the code in pursuit of making it better for interpretation and scanning. Depending on the mask number, there occurs a transformation on the matrix and then the new code is given a penalty score. Our encoder does this as well, it evaluates every mask and determines the `best one`.

2. Decoder
    - 
3. GUI
    - In the encoder section, you can write your own data string and generate a qr code with it. We have also included some buttons to easily load our team name and the ASC course website link.
    - In the decoder section, you can upload an image of a qr code and the decoder will get the data it contains. There is also the option to check the image recognition part of the algorithm.
