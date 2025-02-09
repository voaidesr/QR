
import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from qr.encoder import generateQR
from qr.decoder import full_decode, find_qr_in_image
import qr.constants as constants
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Code Encoder/Decoder GUI")
        self.geometry("1000x800")

        self.encoderFrame = tk.Frame(self, bg="lightblue", width=1000, height=800)
        self.decoderFrame = tk.Frame(self, bg="lightblue", width=1000, height=800)
        self.topBar = tk.Frame(self, bg="lightblue", width=600, height=45, bd=5, relief='ridge')

        self.button1 = tk.Button(self.topBar, text="Encode",
                        padx=5, pady=2, bg='white',
                        command=lambda: self.show_frame(self.encoderFrame))
        self.button2 = tk.Button(self.topBar, text="Decode",
                        padx=5, pady=2, bg='white',
                        command=lambda: self.show_frame(self.decoderFrame))
        self.button1.pack(side='left')
        self.button2.pack(side='right')
        self.topBar.pack(side="top", fill="x")

        self.encoder_frame()
        self.decoder_frame()

        self.current_frame = None
        self.show_frame(self.encoderFrame)

        self.show_rectangle = True
        self.last_file = None

    def generate(self, text_string):
        info = generateQR(text_string)
        if info is None:
            details_text = f"Sorry. Too many characters ({len(text_string)})!\nMax number of characters is 26.\n"
            self.detailsLabel.config(text=details_text)
            return

        for widget in self.imageArea.winfo_children():
            widget.destroy()

        image = Image.open(os.path.join(constants.PROJECT_ROOT,'src', 'qr', 'qr_code.png'))
        image = image.resize((550, 550))
        photo = ImageTk.PhotoImage(image)

        self.qr_image_label = tk.Label(self.imageArea, image=photo)
        self.qr_image_label.pack()
        self.qr_image_label.image = photo

        details_text = (
            f"QR Version: 2 \n"
            f"Error Correction Level: M \n"
            f"Characters entered: {len(text_string)}\n"
            f"Applied Mask: {info['mask']}\n"
            f"Mask Penalty: {info['mask-penalty']}"
        )
        self.detailsLabel.config(text=details_text)

    def encoder_frame(self):
        self.imageArea = tk.Frame(self.encoderFrame, bg='lightblue', bd=5, relief='ridge', width=500)
        self.userArea = tk.Frame(self.encoderFrame, bg='lightblue', bd=5, relief='ridge', width=500)
        self.infoArea = tk.Frame(self.userArea, bg='lightblue', bd=5, relief='ridge', height=300)

        inputLabel = tk.Label(self.userArea, text="Enter the string to encode:", font=("Arial", 12), bg='lightblue')
        inputLabel.pack(pady=5, fill="x", padx=10)

        self.strEntry = tk.Entry(self.userArea, font=("Arial", 12))
        self.strEntry.pack(pady=5, fill="x", padx=10)

        generateButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Generate QR!", command=lambda: self.generate(self.strEntry.get()))
        generateButton.pack(pady=5, fill="y", padx=10)

        teamNameButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Load Team Name", command=lambda: self.update_entry('Get Muxed'))
        teamNameButton.pack(pady=5, fill="y", padx=10)

        linkButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Load ASC link", command=lambda: self.update_entry('cs.unibuc.ro/~crusu/asc/'))
        linkButton.pack(pady=5, fill="y", padx=10)

        downloadButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Download QR code", command=lambda: self.download_qr())
        downloadButton.pack(pady=5, fill="y", padx=10)

        infoLabel = tk.Label(self.infoArea, text = "Information:", font=("Arial", 12), bg='lightblue')
        infoLabel.pack()

        self.detailsLabel = tk.Label(self.infoArea, text = 'QR Version: 2 \n Error Correction Level: M \n', font=('Arial', 12), bg='lightblue')
        self.detailsLabel.pack()

        self.infoArea.pack(side='bottom', fill='both', expand=False)
        self.userArea.pack(side="left", fill="both", expand=False)
        self.imageArea.pack(side="right", fill="both", expand=True)
        self.encoderFrame.pack(fill="both", expand=True)

    def update_entry(self, text):
        self.strEntry.delete(0, tk.END)
        self.strEntry.insert(0, text)
        self.generate(text)

    def download_qr(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg'),
            ('All files', '*.*')
            ],
            title='Save QR Code As',
            initialfile='qr_code.png'
        )

        if file_path:
            try:
                # Copy current QR code to selected location 
                # Set resolution as 250x250 because otherwise the morphological operations will not work
                image = Image.open(os.path.join(constants.PROJECT_ROOT,'src', 'qr', 'qr_code.png'))
                image = image.resize((250, 250))
                image.save(file_path)
                tk.messagebox.showinfo("Success", "QR Code saved successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save QR code: {str(e)}")

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

    def decoder_frame(self):
        self.dec_sideFrame = tk.Frame(self.decoderFrame, bg='lightblue', bd=5, relief='ridge', width=250)
        loadButton = tk.Button(self.dec_sideFrame, text="Load Image", font=("Arial", 12),
                                command=self.load_image)
        loadButton.pack(pady=5, padx=10, fill="x")
        toggleRectButton = tk.Button(self.dec_sideFrame, text="Show/Hide QR Border", font=("Arial", 12),
                                        command=self.toggle_rectangle)
        toggleRectButton.pack(pady=5, padx=10, fill="x")
        example1Button = tk.Button(self.dec_sideFrame, text="Load Team Name", font=("Arial", 12),
                                    command=lambda: self.load_image(os.path.join(constants.PROJECT_ROOT, 'src', 'qr', 'res', 'team_name.png')))
        example1Button.pack(pady=5, padx=10, fill="x")
        example2Button = tk.Button(self.dec_sideFrame, text="Load ASC", font=("Arial", 12),
                                    command=lambda: self.load_image(os.path.join(constants.PROJECT_ROOT, 'src', 'qr', 'res', 'asc.png'))) 
        example2Button.pack(pady=5, padx=10, fill="x")
        example3Button = tk.Button(self.dec_sideFrame, text="Load edge detection example (1)", font=("Arial", 12),
                                    command=lambda: self.load_image(os.path.join(constants.PROJECT_ROOT, 'src', 'qr', 'res', 'page.jpg')))
        example3Button.pack(pady=5, padx=10, fill="x")
        example4Button = tk.Button(self.dec_sideFrame, text="Load edge detection example (2)", font=("Arial", 12),
                                    command=lambda: self.load_image(os.path.join(constants.PROJECT_ROOT, 'src', 'qr', 'res', 'qr.png')))
        example4Button.pack(pady=5, padx=10, fill="x")
        self.dec_sideFrame.pack(side="left", fill="y")

        self.dec_mainFrame = tk.Frame(self.decoderFrame, bg='lightblue', bd=5, relief='ridge')
        self.dec_mainFrame.pack(side="right", fill="both", expand=True)

        self.dec_imageArea = tk.Frame(self.dec_mainFrame, bg='lightblue', bd=5, relief='ridge')
        self.dec_imageArea.pack(side="top", fill="both", expand=True)

        self.dec_textFrame = tk.Frame(self.dec_mainFrame, bg='lightblue', bd=5, relief='ridge')
        self.dec_textFrame.pack(side="top", fill="x")
        infoLabel = tk.Label(self.dec_textFrame, text="Decoded Text:", font=("Arial", 12), bg='lightblue')
        infoLabel.pack(pady=5)
        self.decodedTextLabel = tk.Label(self.dec_textFrame, text="", font=("Arial", 14, "bold"), bg='yellow')
        self.decodedTextLabel.pack(pady=5)


    def load_image(self, file_path=None):
        """
        Opens a file dialog (or uses the provided file path), then detects the QR,
        draws (or not) the QR border based on the toggle, decodes the text, and updates the GUI.
        """
        if file_path is None:
            file_path = filedialog.askopenfilename(
                filetypes=[("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.bmp"))]
            )
        if not file_path:
            return

        self.last_file = file_path
        roi, annotated = find_qr_in_image(file_path, draw_rectangle=self.show_rectangle)
        if roi is None:
            decoded_text = "No valid QR code detected."
        else:
            decoded_text = full_decode(roi)
        self.decodedTextLabel.config(text=decoded_text)

        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(annotated_rgb)
        pil_image = pil_image.resize((550, 550))
        photo = ImageTk.PhotoImage(pil_image)
        for widget in self.dec_imageArea.winfo_children():
            widget.destroy()
        label = tk.Label(self.dec_imageArea, image=photo)
        label.image = photo
        label.pack()

    def toggle_rectangle(self):
        """Toggle the drawing of the QR border on/off and reload the image if one is loaded."""
        self.show_rectangle = not self.show_rectangle
        if self.last_file:
            self.load_image(self.last_file)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
