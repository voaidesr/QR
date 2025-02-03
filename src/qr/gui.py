import tkinter as tk
from PIL import Image, ImageTk 
from qr.encoder import generateQR

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Code Encoder/Decoder GUI")
        self.geometry("1000x665")

        self.encoderFrame = tk.Frame(self, bg="lightblue", width=1000, height=600)
        self.decoderFrame = tk.Frame(self, bg="lightblue", width=1000, height=600)
        self.topBar = tk.Frame(self, bg="lightblue", width=600, height=45, bd=5, relief='ridge')

        self.button1 = tk.Button(self.topBar, text="Encode",
                        padx=5, pady=2, bg='white',command=lambda: self.show_frame(self.encoderFrame))
        
        self.button2 = tk.Button(self.topBar, text="Decode", 
                        padx=5, pady=2, bg='white', command=lambda: self.show_frame(self.decoderFrame))

        self.button1.pack(side='left')
        self.button2.pack(side='right')

        self.topBar.pack(side="top", fill="x")
        self.encoder_frame()    

        self.current_frame = None
        self.show_frame(self.encoderFrame)

    def generate(self, text_string):
        info = generateQR(text_string)
        if info == None:
            details_text = f'Sorry.Too many characters({len(text_string)})!\n Max nmb of characters is 27.\n'
            self.detailsLabel.config(text=details_text)
            return

        for widget in self.imageArea.winfo_children():
            widget.destroy()

        image = Image.open("./qr_code.png")
        image = image.resize((550, 550))
        photo = ImageTk.PhotoImage(image)

        self.qr_image_label = tk.Label(self.imageArea, image=photo)
        self.qr_image_label.pack()
        self.qr_image_label.image = photo

        details_text = f'QR Version: 2 \n Error Correction Level: M \n Characters entered: {len(text_string)}\n Applied Mask: {info['mask']}\n Mask Penalty: {info['mask-penalty']}'
        self.detailsLabel.config(text=details_text)

        
    def encoder_frame(self):
        self.imageArea = tk.Frame(self.encoderFrame, bg='lightblue', bd=5, relief='ridge', width=500)
        self.userArea = tk.Frame(self.encoderFrame, bg='lightblue', bd=5, relief='ridge', width=500)
        self.infoArea = tk.Frame(self.userArea, bg='lightblue', bd=5, relief='ridge', height=300)

        inputLabel = tk.Label(self.userArea, text = "Enter the string to encode:", font=("Arial", 12), bg='lightblue')
        inputLabel.pack(pady=5, fill="x", padx=10)

        self.strEntry = tk.Entry(self.userArea, font=("Arial", 12))
        self.strEntry.pack(pady=5, fill="x", padx=10)

        generateButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Generate QR!", command=lambda: self.generate(self.strEntry.get()))
        generateButton.pack(pady=5, fill="y", padx=10)

        teamNameButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Load Team Name", command=lambda: self.update_entry('Team Name'))
        teamNameButton.pack(pady=5, fill="y", padx=10)

        linkButton = tk.Button(self.userArea, font=("Arial", 12),
                    text="Load ASC link", command=lambda: self.update_entry('cs.unibuc.ro/~crusu/asc/'))
        linkButton.pack(pady=5, fill="y", padx=10)

        infoLabel = tk.Label(self.infoArea, text = "Information:", font=("Arial", 12), bg='lightblue')
        infoLabel.pack()

        self.detailsLabel = tk.Label(self.infoArea, text = 'QR Version: 2 \n Error Correction Level: M \n', font=('Arial', 12), bg='lightblue')
        self.detailsLabel.pack()

        self.infoArea.pack(side='bottom', fill='both', expand=False)
        self.userArea.pack(side="left", fill="both", expand=False)
        self.imageArea.pack(side="right", fill="both", expand=True)

    def update_entry(self, text):
        self.strEntry.delete(0, tk.END)
        self.strEntry.insert(0,text)
        self.generate(text)

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

def main():
    app = App()
    app.mainloop()
