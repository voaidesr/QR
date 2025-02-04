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
    - Imported Pillow and used the `Image` library.
    - Note: In the `Image` library, pixel access is column-first, then row, which is the opposite of matrix access in C.
    - The encoder uses Reed-Solomon error correction. Reed-Solomon error correction relies on polynomial dividing in GF256(Galois-Field 256).
    - The QR code standard specifies 8 masks that can be applied to the qr code. Our encoder does this as well, evaluates every mask and determines the best.
2. GUI
    - In the encoder section, you can write your own data string and generate a qr code with it.
    - In the decoder section, you can upload an image of a qr code and the decoder will get the data it contains.
