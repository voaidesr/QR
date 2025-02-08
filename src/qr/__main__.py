import click
import qr.decoder
from qr.encoder import encode_text
from qr.gui import main

@click.group()
def cli():
    """QR Code Utility"""
    pass

@click.command()
@click.argument("text")
def encode(text: str) -> None:
    """Encode data into a QR code"""
    encode_text(text)

@click.command()
@click.argument("image_path")
def decode(image_path: str) -> None:
    """Decode a QR code"""
    qrCode = qr.decoder.find_qr_in_image(image_path)
    print(qr.decoder.full_decode(qrCode))


@click.command()
def gui():
    main()

cli.add_command(encode)
cli.add_command(decode)
cli.add_command(gui)

if __name__ == "__main__":
    cli()
