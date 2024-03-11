from Analyzer import Analyzer
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time


class Gui:
    def __init__(self):
        self.pdf1_path = ""
        self.pdf2_path = ""
        self.output_path = ""
        self.analyzer = None
    
    def initialize_analyzer(self):
        if not self.analyzer:  # Inizializza solo se non è già stato inizializzato
            self.analyzer = Analyzer(self.pdf1_path)

    def avvia_interfaccia(self):
        self.root = tk.Tk()
        self.root.title("PDF Analyzer")

        self.label1 = tk.Label(self.root, text="PDF 1:")
        self.label1.grid(row=0, column=0)

        self.pdf1_entry = tk.Entry(self.root, width=50)
        self.pdf1_entry.grid(row=0, column=1)

        self.browse_button1 = tk.Button(
            self.root, text="Browse", command=self.browse_pdf1
        )
        self.browse_button1.grid(row=0, column=2)

        self.label2 = tk.Label(self.root, text="PDF 2:")
        self.label2.grid(row=1, column=0)

        self.pdf2_entry = tk.Entry(self.root, width=50)
        self.pdf2_entry.grid(row=1, column=1)

        self.browse_button2 = tk.Button(
            self.root, text="Browse", command=self.browse_pdf2
        )
        self.browse_button2.grid(row=1, column=2)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, columnspan=3)

        self.generate_button = tk.Button(
            self.button_frame, text="PDF", command=self.generate_pdf
        )
        self.generate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.elaborate_button = tk.Button(
            self.button_frame, text="Elaborate", command=self.elaborate_pdfs
        )
        self.elaborate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.time_label = tk.Label(self.root, text="Time: 0:00")
        self.time_label.grid(row=4, column=1)

        self.root.mainloop()

    def browse_pdf1(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if filename:
            self.pdf1_entry.delete(0, tk.END)
            self.pdf1_entry.insert(0, filename)
            self.pdf1_path = filename
            self.output_path = os.path.dirname(filename) + "/"

    def browse_pdf2(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if filename:
            self.pdf2_entry.delete(0, tk.END)
            self.pdf2_entry.insert(0, filename)
            self.pdf2_path = filename

    def elaborate_pdfs(self):
        if not (self.pdf1_path and self.pdf2_path):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        start_time = time.time()
        
        self.initialize_analyzer()
        self.analyzer.elaborate_pdfs(self.pdf2_path, self.output_path)

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time / 60)
        seconds = int(elapsed_time % 60)
        self.time_label.config(text="Time: {:02d}:{:02d}".format(minutes, seconds))

        messagebox.showinfo("Success", f"PDFs saved to {self.output_path}")

    def generate_pdf(self):
        if not (self.pdf1_path):
            messagebox.showerror("Error", "Please fill in PDF1 field.")
            return

        self.initialize_analyzer()
        self.analyzer.generate_pdf(self.output_path)

        messagebox.showinfo(
            "Success", f"Tables created and saved to {self.output_path}"
        )
