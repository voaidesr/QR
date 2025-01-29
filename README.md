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

## Notes

1. Writer
    - Imported Pillow and used the `Image` library.
    - Note: In the `Image` library, pixel access is column-first, then row, which is the opposite of matrix access in C.
