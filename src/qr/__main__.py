import click
from qr.creator import test
from qr.decoder import decode_qr

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
    decode_qr(image_path)

cli.add_command(encode)
cli.add_command(decode)

if __name__ == "__main__":
    cli()
