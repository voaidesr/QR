import click
from qr.creator import test
from qr.decoder import full_decode
from qr.visualizer import QR_Visualizer
from qr.creator import QR_base

@click.group()
def cli():
    """QR Code Utility"""
    pass

@click.command()
def encode():
    """Encode data into a QR code"""
    test()

@click.command()
@click.argument("image_path")
def decode(image_path):
    """Decode a QR code"""
    print(full_decode(image_path))

cli.add_command(encode)
cli.add_command(decode)

if __name__ == "__main__":
    cli()
