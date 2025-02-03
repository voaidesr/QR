import click
import qr.decoder
from qr.encoder import test
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
    qrCode = qr.decoder.find_qr_in_image(image_path)
    print(qr.decoder.full_decode(qrCode))
    qrBase = QR_base(qrCode)

    qrVis = QR_Visualizer(qrBase)
    qrVis.show_image() # BUG: Throws an error

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
