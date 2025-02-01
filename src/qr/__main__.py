import click
from qr.encoder import test
from qr.decoder import full_decode
from qr.visualizer import QR_Visualizer
from qr.encoder import QR_base
from qr.gui import main

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

@click.command()
def gui():
    main()

@click.command()
def gui():
    main()

cli.add_command(encode)
cli.add_command(decode)
cli.add_command(gui)

if __name__ == "__main__":
    cli()
