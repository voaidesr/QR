import tkinter as tk
from qr.encoder import QR_base


def main():
    root = tk.Tk()
    root.geometry("1000x600")
    root.resizable(0,0)

    left_frame = tk.Frame(root, width=500, bd=5, relief=tk.RIDGE)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    right_frame = tk.Frame(root, width=500)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    title = tk.Label(root, text="QR encoder/decoder")
    title.pack(side=tk.TOP)

    root.mainloop()