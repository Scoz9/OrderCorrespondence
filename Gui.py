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
        self.analyzer = Analyzer()

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

        """ self.label3 = tk.Label(self.root, text="Output Path:")
        self.label3.grid(row=2, column=0)

        self.output_path_entry = tk.Entry(self.root, width=50)
        self.output_path_entry.grid(row=2, column=1)

        self.browse_button3 = tk.Button(
            self.root, text="Browse", command=self.browse_output_path
        )
        self.browse_button3.grid(row=2, column=2) """
        
        self.generatePdf = tk.Button(
            self.root, text="generate pdf"
        )
        self.generatePdf.grid(row=3, column=1)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, columnspan=3)
        
        self.generate_button = tk.Button(
        self.button_frame, text="PDF", command=self.generate_pdf)
        self.generate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.elaborate_button = tk.Button(
        self.button_frame, text="Elaborate", command=self.elaborate_pdfs)
        self.elaborate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.time_label = tk.Label(self.root, text="Time: 0:00")
        self.time_label.grid(row=4, column=1)

        self.root.mainloop()

    def browse_pdf1(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf1_entry.delete(0, tk.END)
        self.pdf1_entry.insert(0, filename)
        self.pdf1_path = self.pdf1_entry.get()
        self.output_path = os.path.dirname(self.pdf1_path) + '/'

    def browse_pdf2(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf2_entry.delete(0, tk.END)
        self.pdf2_entry.insert(0, filename)
        self.pdf2_path = self.pdf2_entry.get()

    """ def browse_output_path(self):
        path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, path)
        self.output_path = self.output_path_entry.get() + '/' """

    def elaborate_pdfs(self):
        if not (self.pdf1_path and self.pdf2_path):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        start_time = time.time()
            
        # Estrai le informazioni da "Spedire a:", "Dettagli prodotto" e "Quantita'" dal PDF1
        listOrders = self.analyzer.extract_text_from_pdf(self.pdf1_path)
        
        # Aggiungi il nome del prodotto al PDF2 accanto allo shipping address
        self.analyzer.add_product_name_to_pdf(self.pdf2_path, listOrders)
        
        #Distizione ordini in singleProducts, multiProducts e ordersMultiProducts
        singleProducts, multiProducts, ordersMultiProduct = self.analyzer.categorize_orders(listOrders)
        
        #Raggruppamento singleProducts con stesso nome sommandone le quantita' e raggruppamento multiProducts 
        #con stesso nome e stessa quantita' contando il numero di unita'
        singleProducts, multiProducts = self.analyzer.group_same_products(singleProducts, multiProducts)
        self.analyzer.create_pdf_with_tables(singleProducts, multiProducts, ordersMultiProduct, self.output_path)
        
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time / 60)
        seconds = int(elapsed_time % 60)
        self.time_label.config(text="Time: {:02d}:{:02d}".format(minutes, seconds))

        messagebox.showinfo("Success", f"PDFs saved to {self.output_path}") 
        
    def generate_pdf(self):
        if not (self.pdf1_path):
            messagebox.showerror("Error", "Please fill in PDF1 field.")
            return

        # Estrai le informazioni da "Spedire a:" e "Dettagli prodotto" dal PDF1
        listOrders = self.analyzer.extract_text_from_pdf(self.pdf1_path)
        singleProducts, multiProducts, ordersMultiProduct = self.analyzer.categorize_orders(listOrders)
        singleProducts, multiProducts = self.analyzer.group_same_products(singleProducts, multiProducts)
        
        self.analyzer.create_pdf_with_tables(singleProducts, multiProducts, ordersMultiProduct, self.output_path)
            
        messagebox.showinfo("Success", f"Tables created and saved to {self.output_path}")